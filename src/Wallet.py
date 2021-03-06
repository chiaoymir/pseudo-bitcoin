# standard modules
import hashlib
import json
import base64
import base58
# third-party ecdsa modules
from ecdsa import SigningKey, VerifyingKey, NIST384p
from Crypto.Hash import RIPEMD160


class WalletPool:
    """
    A class for managing wallets in the blockchain.

    ...

    Attributes:
    ----------
    wallets : List[Wallet]
        the wallets in the wallet pool

    size : int 
        the number of wallets in the wallet pool

    Methods:
    ----------
    get_wallet(address) : Wallet
        get wallet of the given address

    has_address(address) : bool
        check if we have this wallet in the wallet pool

    add_wallet(wallet) : None
        add a wallet in the wallet pool

    remove_address(address) : wallet
        remove a wallet of the given address and then return it

    has_balance(address, amount) : bool
        check if a wallet has enough amount of balance

    add_balance(address, amount) : None
        add amount of balance into a wallet

    sub_balance(address, amount) : None
        substract amount of balance from a wallet

    wallet_balance(address) : int
        get the balance of the wallet

    get_wallet_signing_key(address) : SigningKey
        get the signing key of a wallet

    get_wallet_verifying_key(address) : VerifyingKey
        get the verifying key of a wallet
    """

    def __init__(self):
        self._wallets = dict()

    @property
    def wallets(self):
        """The wallets in the wallet pool

        Returns:
        ----------
        wallets : List[tuple]
            return a list contains (address, wallet) tuple of each wallet
        """
        return self._wallets.items()

    @property
    def size(self):
        """The number of wallets in the wallet pool

        Returns:
        ----------
        size : int
            the number of wallets
        """
        return len(self._wallets.keys())

    def get_wallet(self, address):
        """Get the wallet of the given address

        Parameters:
        ----------
        address : Wallet.address (str)
            the wallet address

        Returns:
        ----------
        wallet : Wallet
            the wallet of the given address
        """
        return self._wallets[address]

    def has_address(self, address):
        """Check if the wallet exists

        Parameters:
        ----------
        address : Wallet.address (str)
            the wallet address

        Returns:
        ----------
        result : bool
            the result of whether the wallet is in the wallet pool
        """
        return address in self._wallets

    def add_wallet(self, wallet):
        """Add a wallet in the wallet pool

        Parameters:
        ----------
        wallet : Wallet 
            the wallet to be added
        """
        self._wallets[wallet.address] = wallet

    def remove_address(self, address):
        """Remove a wallet based on the given address

        Parameters:
        ----------
        address : Wallet.address (str)
            the wallet address to be removed

        Returns:
        ----------
        wallet : Wallet
            the removed wallet instance, return None if not found
        """
        return self._wallets.pop(address, None)

    def has_balance(self, address, amount):
        """Check if the wallet has enough balance"""
        return self._wallets[address].balance >= amount

    def add_balance(self, address, amount):
        """Add amount of balance to a wallet

        Parameters:
        ----------
        address : Wallet.address (str)
            the wallet address

        amount : int
            the amount of value to be added to the wallet
        """
        wallet = self._wallets[address]
        wallet.add_balance(amount)

    def sub_balance(self, address, amount):
        """Subtract amount of balance from a wallet

        Parameters:
        ----------
        address : Wallet.address (str)
            the wallet address

        amount : int
            the amount of value to be subtracted from the wallet
        """
        wallet = self._wallets[address]
        wallet.sub_balance(amount)

    def wallet_balance(self, address):
        """Get the balance of a wallet

        Paremeters:
        ----------
        address : Wallet.address (str)
            the wallet address

        Returns:
        ----------
        balance : int
            the wallet balance
        """
        return self._wallets[address].balance

    def get_wallet_signing_key(self, address):
        """Get the signing key of a wallet

        Parameters:
        ----------
        address : Wallet.address (str)
            the wallet address

        Returns:
        ----------
        sk : SigningKey
            the wallet signing key (private key)
        """
        wallet = self._wallets[address]
        return wallet.signing_key

    def get_wallet_verifying_key(self, address):
        """Get the verifying key of a wallet

        Parameters:
        ----------
        address : Wallet.address (str)
            the wallet address

        Returns:
        ----------
        vk : VerifyingKey
            the wallet verifying key (public key)
        """
        wallet = self._wallets[address]
        return wallet.verifying_key


class Wallet:
    """
    A class represent the wallet data in the blockchain.

    ... 

    Attributes:
    ----------
    name : str 
        the name of the wallet

    balance : int 
        the wallet balance

    sk : SigningKey
        the signing key (private key) of the account

    vk : VerifyingKey
        the verifying key (public key) of the account

    address : str
        the address of the wallet

    Methods: 
    ----------
    add_balance(amount) : None
        add the amount to the wallet balance

    sub_balance(amount) : None
        subtract the amount from the wallet balance


    Static Methods:
    ----------
    verify_address(wallet) : bool
        verify whether wallet has the valid address

    serialize(wallet) : str
        transform a wallet into a string

    deserialize(raw_data) : Wallet
        transform a string back into a wallet
    """

    def __init__(self, name, balance=0):
        """
        Parameters: 
        ----------
        name : str
            the name of the account

        balance : int 
            the account balance
        """
        self._name = name
        self._balance = balance
        self.sk = SigningKey.generate(curve=NIST384p)
        self.vk = self.sk.verifying_key
        self._address = self._create_address()

    @property
    def name(self):
        """The account name of the wallet"""
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def balance(self):
        """The account balance of the wallet"""
        return self._balance

    @balance.setter
    def balance(self, balance):
        self._balance = balance

    @property
    def signing_key(self):
        """The signing key (private key) of the wallet"""
        return self.sk

    @property
    def verifying_key(self):
        """The verifying key (public key) of the wallet"""
        return self.vk

    @property
    def address(self):
        """The account address of the wallet"""
        return self._address

    @address.setter
    def address(self, address):
        self._address = address

    def add_balance(self, amount):
        """Add the amount to the wallet balance

        Parameters: 
        ----------
        amount : int
            the amount to be added to the balance
        """
        self.balance += amount

    def sub_balance(self, amount):
        """Substract the amount from the wallet balance

        Parameters: 
        ----------
        amount : int
            the amount to be substracted form the wallet balance
        """
        self.balance -= amount

    def _create_address(self):
        """Create the address of the wallet

        Returns:
        ----------
        addr : str
            the address of the wallet
        """

        # Initialize
        m = hashlib.sha256()
        h = RIPEMD160.new()
        vk = base64.b64encode(self.verifying_key.to_string())

        # Compute the hash of the wallet public key
        m.update(vk)
        h.update(m.digest())
        key_hash = h.digest()

        # Compute checksum
        # Create the sha256 hash of the key_hash
        m = hashlib.sha256()
        m.update(key_hash)
        temp = m.digest()

        # Hash again
        m = hashlib.sha256()
        m.update(temp)
        checksum = m.digest()

        # Concatenate two string
        addr = key_hash + checksum

        return base58.b58encode(addr).decode()

    @staticmethod
    def verify_address(wallet):
        """Verify the address of a wallet

        Parameters:
        ----------
        wallet : Wallet
            the account wallet

        Returns:
        ----------
        result : bool
            the result of whether the the wallet has valid address
        """
        # Initialize
        m = hashlib.sha256()
        h = RIPEMD160.new()
        vk = base64.b64encode(wallet.verifying_key.to_string())

        # Create the sha256 hash of the wallet public key
        m.update(vk)
        key_hash = h.update(m.digest())

        # Compute checksum
        # Create the sha256 of the key_hash
        m = hashlib.sha256()
        m.update(key_hash)
        temp = m.digest()

        # Hash again
        m = hashlib.sha256()
        m.update(temp)
        checksum = m.digest()

        # Concatenate two string
        addr = key_hash + checksum

        return addr == wallet.address

    @staticmethod
    def serialize(wallet):
        """Transform a wallet into a string

        Parameters:
        ----------
        wallet : Wallet
            the account wallet

        Returns:
        ----------
        data : str
            the serialized wallet data
        """
        # Creake a dictionary storing the information of the wallet
        d = {'name': wallet.name, 'balance': wallet.balance, 'sk': base64.b64encode(wallet.signing_key.to_string(
        )).decode(), 'vk': base64.b64encode(wallet.verifying_key.to_string()).decode(), 'address': wallet.address}

        # Transform the dictionary into a string
        data = json.dumps(d)

        return data

    @staticmethod
    def deserialize(raw_data):
        """Transform a string back into a wallet

        Parameters:
        ----------
        raw_data : str
            the json formatted string representation of a wallet

        Returns:
        ----------
        wallet : Wallet
            a wallet instance
        """
        # Process the raw data
        data = json.loads(raw_data)

        # Create a wallet with the given data
        wallet = Wallet(data['name'], data['balance'])
        wallet.sk = SigningKey.from_string(
            base64.b64decode(data['sk'].encode()), curve=NIST384p)
        wallet.vk = VerifyingKey.from_string(
            base64.b64decode(data['vk'].encode()), curve=NIST384p)
        wallet.address = data['address']

        return wallet
