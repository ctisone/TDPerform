#************
# Imports
#************
import json


class TdaConfig:
    """ Encapsulates the configuration files used by the program """

    def __init__(self, settingsFileName: str, secretsFileName : str) -> None:
        """ Class constructor. Reads and parses the secrets JSON file.

        Parameters
        ----------
        settingsFileName:  Fully pathed name of the settings JSON file.
        secretsFileName:  Fully pathed name of the secrets JSON file.
        
        Returns
        -------
        None.
        """
        with open(settingsFileName, "rt") as jsonFile:
            self.__settings = json.loads(jsonFile.read())
        with open(secretsFileName, "rt") as jsonFile:
            self.__secrets = json.loads(jsonFile.read())
        return

    def getOAuthTokenFileName(self) -> str:
        """ Retrieves the oAuth token file name from the secrets file.

        Parameters
        ----------
        None.
        
        Returns
        -------
        The name of the oAuth token file.
        """
        return(self.__secrets["tokenFile"])

    def getApiKey(self) -> str:
        """  Retrieves the account API key from the secrets file.

        Parameters
        ----------
        None.
        
        Returns
        -------
        The TD Ameritrade account number.
        """
        return(self.__secrets["apiKey"])

    def getRedirectUri(self) -> str:
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

    def getAccountNumber(self) -> int:
        """  Retrieves the TD Ameritrade account number from the secrets file.

        Parameters
        ----------
        None.
        
        Returns
        -------
        The TD Ameritrade account number.
        """
        return(self.__secrets["accountNumber"])

    def getMongoConnectionString(self) -> str:
        """  Retrieves the MongoDB connection string from the secrets file.

        Parameters
        ----------
        None.
        
        Returns
        -------
        The MongoDB connection string.
        """
        return(self.__settings["mongoConnection"])
