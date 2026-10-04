"""
KALATRACE Boot System

Responsible for starting and preparing
the Kernel environment.
"""


from kernel.kernel import Kernel



class KernelBoot:
    """
    Controls the Kernel startup sequence.
    """


    def __init__(
        self
    ):

        self.kernel = None



    def boot(
        self
    ) -> Kernel:
        """
        Starts the KALATRACE Kernel.
        """

        if self.kernel is not None:

            return self.kernel


        self.kernel = Kernel()


        self.kernel.initialize()


        self.kernel.start()


        return self.kernel



    def shutdown(
        self
    ):
        """
        Shuts down the Kernel.
        """

        if self.kernel is None:

            return


        self.kernel.stop()


        self.kernel = None