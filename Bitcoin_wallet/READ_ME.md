# Bitcoin_wallet

![Bitcoin](https://img.shields.io/badge/Bitcoin-Currency-orange?logo=bitcoin&style=flat-square)
![C#](https://img.shields.io/badge/C%23-Language-blue?logo=csharp&style=flat-square)
![Visual Studio](https://img.shields.io/badge/Visual%20Studio-IDE-purple?logo=visualstudio&style=flat-square)
![NuGet](https://img.shields.io/nuget/v/NBitcoin?color=blue&logo=nuget&style=flat-square)
![NBitcoin](https://img.shields.io/badge/NBitcoin-Library-green?style=flat-square&logo=bitcoin)

Bitcoin_wallet is a simple command-line interface (CLI) application designed to interact with Bitcoin wallets. It provides users with basic wallet operations, including scanning a wallet, generating a new wallet, and sending Bitcoin. 

## Features

- **Scan a Bitcoin Wallet**: Retrieve information from an existing Bitcoin wallet.
- **Generate a New Wallet**: Create a brand new Bitcoin wallet with a private and public key.
- **Send Bitcoin**: Send Bitcoin from one wallet to another with ease.

## Getting Started

### Prerequisites

Before you start using Bitcoin_wallet, ensure you have the following installed:

- [.NET Framework 4.7.2](https://dotnet.microsoft.com/download/dotnet-framework/net472) or higher
- [Git](https://git-scm.com/) for version control (optional)

### Installation

1. Clone the **Bitcoin_wallet** directory only to your local machine:

   ```bash
   git clone --depth 1 --filter=blob:none --sparse https://github.com/yahyamissaoui/My_Projects.git
   cd My_Projects
   git sparse-checkout init --cone
   git sparse-checkout set Bitcoin_wallet
   ```
2. Navigate to the Bitcoin_wallet directory:
   
   ```bash
   cd Bitcoin_wallet
   ```
3. Run the installer:

   Go to the App folder and locate the `Bitcoin_wallet.exe` file in the `Bitcoin_wallet\` directory and run it to install the application on your system
   and test it yourself.

### Command-Line Interface

Bitcoin_wallet provides a simple command-line interface. Once the application is running, you can access the following options:

1. **Scan a Wallet**  
   Use this option to scan an existing Bitcoin wallet by providing the wallet address.

2. **Generate a New Wallet**  
   This will generate a new Bitcoin wallet with a unique private and public key.

3. **Send Bitcoin**  
   Send Bitcoin from one wallet to another by specifying the recipient's wallet address, the amount, and other necessary transaction details.



## Contributing

If you'd like to contribute to this project, feel free to fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For more information, feel free to reach out to [Yahya Missaoui](https://github.com/yahyamissaoui).
