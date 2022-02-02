#************
# Imports
#************
import json
import os


class TdaConfig:
    """ Encapsulates the configuration files used by the program """

    def __init__(self, settingsFileName: str) -> None:
        """ Class constructor. Reads and parses the secrets JSON file.

        Parameters
        ----------
        settingsFileName:  Fully pathed name of the settings JSON file.
        
        Returns
        -------
        None.
        """
        with open(settingsFileName, "rt") as jsonFile:
            self.__settings = json.loads(jsonFile.read())

        # Patch the names of files specified on the settings file to be absolute pathed
        self.__settings["oAuthFile"] = TdaConfig._patchFileName(self.__settings["oAuthFile"], settingsFileName)
        self.__settings["secretsFile"] = TdaConfig._patchFileName(self.__settings["secretsFile"], settingsFileName)

        # Now read the secrets file
        with open(self.__settings["secretsFile"], "rt") as jsonFile:
            self.__secrets = json.loads(jsonFile.read())
        return

    @property
    def oAuthTokenFileName(self) -> str:
        """ Retrieves the oAuth token file name from the secrets file.

        Parameters
        ----------
        None.
        
        Returns
        -------
        The name of the oAuth token file.
        """
        return(self.__settings["oAuthFile"])

    @property
    def apiKey(self) -> str:
        """  Retrieves the account API key from the secrets file.

        Parameters
        ----------
        None.
        
        Returns
        -------
        The TD Ameritrade account number.
        """
        return(self.__secrets["apiKey"])

    @property
    def redirectUri(self) -> str:
        """  Retrieves the oAuth redirect URI from the secrets file.  This must match the URI used when
            setting up the API key.

        Parameters
        ----------
        None.
        
        Returns
        -------
        The oAuth redirect URI string.
        """
        return(self.__secrets["redirectURI"])

    @property
    def accountNumber(self) -> int:
        """  Retrieves the TD Ameritrade account number from the secrets file.

        Parameters
        ----------
        None.
        
        Returns
        -------
        The TD Ameritrade account number.
        """
        return(self.__secrets["accountNumber"])

    @property
    def mongoConnectionString(self) -> str:
        """  Retrieves the MongoDB connection string from the secrets file.

        Parameters
        ----------
        None.
        
        Returns
        -------
        The MongoDB connection string.
        """
        return(self.__settings["mongoConnection"])

    @staticmethod
    def _patchFileName(fileName: str, refFileName: str) -> str:
        """  Patches a file name pulled from a configuration file so that the resulting file name has
            an absolute path.  If the read file name is already specified with an absolute path, it
            in unchanged.  Otherwise, the file and its path are considered relative to the config
            file from where it was read and the resulting absolute pathed name is returned.

        Parameters
        ----------
        fileName:  The file name retrieved from a config file.
        refFileName:  The fully pathed file name to the file from which fileName was read.
        
        Returns
        -------
        The file name absolute path.
        """
        if(not os.path.isabs(fileName)):
            fileName = os.path.normpath(os.path.join(os.path.dirname(refFileName), fileName))
        return(fileName)
