#************
# Imports
#************
import argparse
from typing import List

class AppArgParser(argparse.ArgumentParser):
    """ Encapsulates command line argument parsing """

    def __init__(self, cliArgs: List[str]) -> None:
        """ Class constructor.  Sets up the argparser object and parses the passed in command line arguments.
    
        Parameters
        ----------
        cliArgs: The command line arguments to parse.  These must not include the arg[0] received
            by main(), which is the module name being run.

        Returns
        -------
        None.
        """
        super().__init__(description = "Downloads and processes transaction data from your TD Ameritrade account")

        # Add the program version
        self.version = "0.0.1"

        # Add positional arguments
        self.add_argument("settings", help = "Specify the JSON configuration file")

        # Add optional arguments
        self.add_argument("-v", action = "version", help = "Shows the version and exits")
        self.add_argument("-Dt", action = "store_true", help = "Causes all stored transaction data to be deleted")
        self.add_argument("-Dp", action = "store_true", help = "Causes all stored position data to be deleted")

        # Parse it all
        self.__namespace = self.parse_args(cliArgs)
        return

    @property
    def settingsFileName(self) -> str:
        """ Retrieves the name of the JSON settings file.  This file contains various settings and options
            that are not sensitive.
    
        Parameters
        ----------
        None.

        Returns
        -------
        The name of the settings JSON file.
        """
        return(self.__namespace.settings)

    @property
    def deleteTransactions(self) -> bool:
        """ Determines if the command line specifies that all downloaded transaction data is to be deleted.
    
        Parameters
        ----------
        None.

        Returns
        -------
        True if downloaded transaction data is to be deleted.
        """
        return(self.__namespace.Dt)

    @property
    def deletePositions(self) -> bool:
        """ Determines if the command line specifies that all derived position data is to be deleted.
    
        Parameters
        ----------
        None.

        Returns
        -------
        True if derived position data is to be deleted.
        """
        return(self.__namespace.Dp)