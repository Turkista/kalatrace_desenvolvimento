"""
KALATRACE Command Center Tests

Tests command lifecycle management.
"""


import pytest


from core.command import (

    CommandStatus,

    CommandRegistry,

    CommandManager,

    CommandQueue,

    CommandDispatcher,

    CommandExecutor,

    CommandService

)



# =====================================================
# Test Executor
# =====================================================


class TestExecutor(CommandExecutor):
    """
    Fake executor implementation
    used for command tests.
    """


    @property
    def name(self):

        return "test_executor"



    def execute(
        self,
        command
    ):
        """
        Executes fake command.
        """

        return {

            "command_id": command.command_id,

            "status": "EXECUTED"

        }



# =====================================================
# Fixtures
# =====================================================


@pytest.fixture
def command_environment():

    registry = CommandRegistry()


    manager = CommandManager(
        registry
    )


    queue = CommandQueue()


    dispatcher = CommandDispatcher()


    executor = TestExecutor()


    dispatcher.register_executor(
        "test_executor",
        executor
    )


    service = CommandService(

        registry,

        manager,

        queue,

        dispatcher

    )


    return (

        service,

        registry,

        queue

    )


# =====================================================
# Creation
# =====================================================


def test_create_command(
    command_environment
):

    service, registry, queue = command_environment


    command = service.create_command(

        name="Test Command",

        objective="Validate command creation"

    )


    assert command is not None


    assert command.name == "Test Command"



    stored = registry.get(

        command.command_id

    )


    assert stored == command




# =====================================================
# Queue
# =====================================================


def test_enqueue_command(
    command_environment
):

    service, registry, queue = command_environment


    command = service.create_command(

        name="Queue Test",

        objective="Validate queue"

    )


    service.enqueue_command(

        command.command_id

    )


    assert queue.size() == 1




# =====================================================
# Execution
# =====================================================


def test_execute_command(
    command_environment
):

    service, registry, queue = command_environment


    command = service.create_command(

        name="Execution Test",

        objective="Validate execution"

    )


    service.enqueue_command(

        command.command_id

    )


    result = service.execute_command(

        command.command_id,

        executor="test_executor"

    )


    assert result is not None


    assert result["status"] == "EXECUTED"




# =====================================================
# Completion
# =====================================================


def test_complete_command(
    command_environment
):

    service, registry, queue = command_environment


    command = service.create_command(

        name="Complete Test",

        objective="Validate completion"

    )


    service.enqueue_command(

        command.command_id

    )


    service.execute_command(

        command.command_id,

        executor="test_executor"

    )


    completed = service.complete_command(

        command.command_id

    )


    assert completed.status == CommandStatus.COMPLETED




# =====================================================
# Failure
# =====================================================


def test_fail_command(
    command_environment
):

    service, registry, queue = command_environment


    command = service.create_command(

        name="Failure Test",

        objective="Validate failure"

    )


    failed = service.fail_command(

        command.command_id

    )


    assert failed.status == CommandStatus.FAILED




# =====================================================
# Invalid transition
# =====================================================


def test_invalid_transition():


    from core.command.command_status import (

        CommandStateMachine

    )


    with pytest.raises(ValueError):


        CommandStateMachine.transition(

            CommandStatus.CREATED,

            CommandStatus.COMPLETED

        )




# =====================================================
# History
# =====================================================


def test_command_history(
    command_environment
):

    service, registry, queue = command_environment


    command = service.create_command(

        name="History Test",

        objective="Validate history"

    )


    history = service.get_history(

        command.command_id

    )


    assert history is not None


    assert len(

        history.events

    ) >= 1