"""The periodic catalog sync must not run on the request event loop.

`TensorZeroSeeder.seed` is declared `async` and is blocking throughout: it calls
`CatalogClient().fetch_catalog_sync()` and then performs roughly 1500 synchronous upserts.
Awaited directly, it starves the loop, `/health` stops answering, and the liveness probe
(10s period, 10s timeout, 3 failures) kills the container about thirty seconds in.

That is not hypothetical. It was observed in budconnect-dev: a SIGKILL (exit 137) mid-sync,
`Liveness probe failed: context deadline exceeded` in the events, and `Empty reply from
server` at the caller. The effect is that the 24h refresh binding cannot complete on ANY
install -- prices stay as fresh as the last successful startup seed and no further.

These tests read the source rather than calling the endpoint: `budconnect.model.routes`
pulls in the ORM and the auth stack and cannot be imported standalone.
"""

import ast
import pathlib

import pytest


ROUTES = pathlib.Path(__file__).parent.parent / "budconnect" / "model" / "routes.py"


@pytest.fixture(scope="module")
def tree() -> ast.Module:
    """Parse the routes module once for the tests in this file."""
    return ast.parse(ROUTES.read_text())


def _function(tree: ast.Module, name: str) -> ast.AST:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"{name} not found in {ROUTES.name}")


def _calls(node: ast.AST) -> list[str]:
    """Dotted names of everything called inside *node*."""
    out = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            out.append(ast.unparse(sub.func))
    return out


def test_the_sync_endpoint_offloads_to_a_thread(tree):
    """The fix itself: the blocking seed is handed to a worker thread."""
    handler = _function(tree, "handle_tensorzero_sync")
    assert "asyncio.to_thread" in _calls(handler), (
        "the sync must be handed to a worker thread; awaited on the request loop it stops "
        "/health answering and the liveness probe kills the container mid-sync"
    )


def test_the_sync_endpoint_does_not_await_the_seeder_directly(tree):
    """The specific regression: `await TensorZeroSeeder().seed()`.

    It reads as correct -- it is an await on an async function -- which is exactly why this
    needs a test rather than review.
    """
    handler = _function(tree, "handle_tensorzero_sync")
    for node in ast.walk(handler):
        if isinstance(node, ast.Await):
            awaited = ast.unparse(node.value)
            assert "seed()" not in awaited or "to_thread" in awaited, (
                f"awaits {awaited!r} on the request loop; wrap it in asyncio.to_thread"
            )


def test_the_worker_runs_the_seeder_in_its_own_loop(tree):
    """A thread has no running loop, so the coroutine needs `asyncio.run` to execute."""
    worker = _function(tree, "_run_tensorzero_seed_blocking")
    calls = _calls(worker)
    assert "asyncio.run" in calls, "the worker must drive the coroutine with asyncio.run"
    assert any("TensorZeroSeeder" in c for c in calls), "the worker must run the seeder"


def test_the_overlap_lock_is_still_held_across_the_offload(tree):
    """Threading the work must not drop the guard against concurrent runs.

    The dapr binding fires every 24h and a run can be triggered by hand; two seeders
    upserting the same rows at once is how the catalog ends up interleaved.
    """
    handler = _function(tree, "handle_tensorzero_sync")
    source = ast.unparse(handler)
    assert "_tensorzero_sync_lock" in source
    assert "async with _tensorzero_sync_lock" in source
    # the offload has to happen INSIDE the lock, not before or after it
    withs = [n for n in ast.walk(handler) if isinstance(n, ast.AsyncWith)]
    assert withs, "the lock is no longer taken with `async with`"
    assert any("asyncio.to_thread" in _calls(w) for w in withs), (
        "the offload must sit inside the lock, otherwise two syncs can overlap"
    )


def test_a_failed_sync_answers_an_error_status(tree):
    """A 200 with "error" in the body is a delivered event to Dapr.

    A sync that refused a truncated catalog, or crashed, looked identical to a good one
    everywhere but this process's own log.
    """
    handler = _function(tree, "handle_tensorzero_sync")
    raises = [ast.unparse(n.exc) for n in ast.walk(handler) if isinstance(n, ast.Raise) and n.exc is not None]
    assert any("HTTPException" in r and "HTTP_500" in r for r in raises), raises
    for node in ast.walk(handler):
        if isinstance(node, ast.Return) and node.value is not None:
            assert "'error'" not in ast.unparse(node.value), "a failure is returned as a 200"


def test_the_error_is_raised_after_the_lock_is_released(tree):
    """The failure is raised after the lock is released.

    Raised inside `async with` it would still release, but a reader should not have to
    reason about that.
    """
    handler = _function(tree, "handle_tensorzero_sync")
    for w in (n for n in ast.walk(handler) if isinstance(n, ast.AsyncWith)):
        assert not any(isinstance(n, ast.Raise) for n in ast.walk(w))


SEEDER = ROUTES.parent.parent / "seeders" / "tensorzero.py"


def test_the_seeder_keeps_its_own_failure_messages():
    """A SeederException reaches the cron response with its own message.

    `seed()` ends in `except Exception`, which re-wraps as "Unexpected error during
    TensorZero seeding". SeederException is an Exception subclass, so without an earlier
    `except SeederException: raise` every guard's explanation was replaced by that.
    """
    seed = next(
        n for n in ast.walk(ast.parse(SEEDER.read_text())) if isinstance(n, ast.AsyncFunctionDef) and n.name == "seed"
    )
    handlers = next(n for n in ast.walk(seed) if isinstance(n, ast.Try)).handlers
    names = [ast.unparse(h.type) for h in handlers]
    assert names[0] == "SeederException", names
    assert isinstance(handlers[0].body[-1], ast.Raise) and handlers[0].body[-1].exc is None
