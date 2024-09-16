using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using NBitcoin;
using Newtonsoft.Json.Linq;

namespace BitcoinWallet
{
    class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("Welcome to the Simple Bitcoin Wallet");
            Console.WriteLine("-------------------------------------");

            // Main loop
            while (true)
            {
                Console.WriteLine("\nPlease select an option:");
                Console.WriteLine("1. Generate New Wallet");
                Console.WriteLine("2. Check Balance");
                Console.WriteLine("3. Send Bitcoin");
                Console.WriteLine("4. Exit");
                Console.Write("Enter your choice (1-4): ");
                string choice = Console.ReadLine();

                switch (choice)
                {
                    case "1":
                        GenerateNewWallet();
                        break;
                    case "2":
                        await CheckBalance();
                        break;
                    case "3":
                        await SendBitcoin();
                        break;
                    case "4":
                        Console.WriteLine("Exiting the application. Goodbye!");
                        return;
                    default:
                        Console.WriteLine("Invalid choice. Please select a valid option.");
                        break;
                }
            }
        }

        /// <summary>
        /// Generates a new Bitcoin wallet (private key and public address).
        /// </summary>
        static void GenerateNewWallet()
        {
            // Generate a new random private key
            Key privateKey = new Key(); // generates a random private key
            BitcoinSecret secret = privateKey.GetBitcoinSecret(Network.Main);

            // Get the corresponding public address
            BitcoinAddress address = secret.GetAddress(ScriptPubKeyType.Legacy);

            Console.WriteLine("\n--- New Bitcoin Wallet Generated ---");
            Console.WriteLine($"Private Key (WIF): {secret}");
            Console.WriteLine($"Public Address: {address}");
            Console.WriteLine("------------------------------------");
            Console.WriteLine("** IMPORTANT: Store your private key securely! **");
        }

        /// <summary>
        /// Prompts the user to enter a Bitcoin address and displays its balance.
        /// </summary>
        static async Task CheckBalance()
        {
            Console.Write("\nEnter the Bitcoin address to check balance: ");
            string addressInput = Console.ReadLine();

            // Validate the Bitcoin address using BitcoinAddress.Create
            BitcoinAddress address;
            try
            {
                address = BitcoinAddress.Create(addressInput, Network.Main);
            }
            catch (FormatException)
            {
                Console.WriteLine("Invalid Bitcoin address format.");
                return;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An error occurred while parsing the address: {ex.Message}");
                return;
            }

            decimal balance = await GetBitcoinBalance(address.ToString());
            Console.WriteLine($"\nBalance for {address}: {balance} BTC");
        }

        /// <summary>
        /// Sends Bitcoin from the user's wallet to a specified recipient.
        /// </summary>
        static async Task SendBitcoin()
        {
            Console.Write("\nEnter your Private Key (WIF): ");
            string privateKeyWif = Console.ReadLine();

            BitcoinSecret secret;
            try
            {
                secret = new BitcoinSecret(privateKeyWif, Network.Main);
            }
            catch (Exception)
            {
                Console.WriteLine("Invalid private key format.");
                return;
            }

            BitcoinAddress fromAddress = secret.GetAddress(ScriptPubKeyType.Legacy);
            Console.WriteLine($"From Address: {fromAddress}");

            Console.Write("Enter recipient address: ");
            string toAddressInput = Console.ReadLine();

            // Validate the recipient Bitcoin address using BitcoinAddress.Create
            BitcoinAddress toAddress;
            try
            {
                toAddress = BitcoinAddress.Create(toAddressInput, Network.Main);
            }
            catch (FormatException)
            {
                Console.WriteLine("Invalid recipient Bitcoin address format.");
                return;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An error occurred while parsing the recipient address: {ex.Message}");
                return;
            }

            Console.Write("Enter amount in BTC: ");
            string amountInput = Console.ReadLine();
            if (!decimal.TryParse(amountInput, out decimal amount) || amount <= 0)
            {
                Console.WriteLine("Invalid amount entered.");
                return;
            }

            string txId = await SendBitcoinTransaction(secret, toAddress.ToString(), amount);
            if (!string.IsNullOrEmpty(txId))
            {
                Console.WriteLine($"Transaction successfully sent. TXID: {txId}");
            }
            else
            {
                Console.WriteLine("Transaction failed.");
            }
        }

        /// <summary>
        /// Retrieves the balance of a given Bitcoin address using BlockCypher's API.
        /// </summary>
        /// <param name="address">The Bitcoin address.</param>
        /// <returns>The balance in BTC.</returns>
        static async Task<decimal> GetBitcoinBalance(string address)
        {
            string url = $"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance";
            using (HttpClient client = new HttpClient())
            {
                try
                {
                    var response = await client.GetAsync(url);
                    if (response.IsSuccessStatusCode)
                    {
                        var json = await response.Content.ReadAsStringAsync();
                        dynamic data = JObject.Parse(json);
                        long satoshis = data.balance;
                        decimal btc = satoshis / 100000000m;
                        return btc;
                    }
                    else
                    {
                        Console.WriteLine("Error fetching balance.");
                        return 0;
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Exception occurred: {ex.Message}");
                    return 0;
                }
            }
        }

        /// <summary>
        /// Sends Bitcoin from the user's wallet to a specified recipient.
        /// </summary>
        /// <param name="secret">The user's Bitcoin secret (private key).</param>
        /// <param name="toAddress">The recipient's Bitcoin address.</param>
        /// <param name="amount">The amount to send in BTC.</param>
        /// <returns>The transaction ID (TXID) if successful; otherwise, null.</returns>
        static async Task<string> SendBitcoinTransaction(BitcoinSecret secret, string toAddress, decimal amount)
        {
            // Convert amount to satoshis
            long satoshisToSend = (long)(amount * 100000000m);

            // Fetch UTXOs
            string utxoUrl = $"https://api.blockcypher.com/v1/btc/main/addrs/{secret.GetAddress(ScriptPubKeyType.Legacy)}/full?limit=50";
            using (HttpClient client = new HttpClient())
            {
                try
                {
                    var utxoResponse = await client.GetAsync(utxoUrl);
                    if (!utxoResponse.IsSuccessStatusCode)
                    {
                        Console.WriteLine("Error fetching UTXOs.");
                        return null;
                    }

                    var utxoJson = await utxoResponse.Content.ReadAsStringAsync();
                    dynamic utxoData = JObject.Parse(utxoJson);
                    var utxos = utxoData.txrefs;

                    if (utxos == null)
                    {
                        Console.WriteLine("No UTXOs available.");
                        return null;
                    }

                    // Select UTXOs
                    Money total = Money.Zero;
                    var coins = new List<Coin>();

                    foreach (var utxo in utxos)
                    {
                        string txId = utxo.tx_hash;
                        int vout = utxo.tx_output_n;
                        long satoshis = utxo.value;

                        var outPoint = new OutPoint(uint256.Parse(txId), vout);
                        var scriptPubKey = secret.GetAddress(ScriptPubKeyType.Legacy).ScriptPubKey;
                        var txOut = new TxOut(Money.Satoshis(satoshis), scriptPubKey);
                        var coin = new Coin(outPoint, txOut);
                        coins.Add(coin);
                        total += Money.Satoshis(satoshis);

                        if (total.ToUnit(MoneyUnit.BTC) >= amount + 0.0001m) // Adding a fixed fee
                            break;
                    }

                    if (total.ToUnit(MoneyUnit.BTC) < amount + 0.0001m)
                    {
                        Console.WriteLine("Insufficient funds.");
                        return null;
                    }

                    // Create transaction
                    //TransactionBuilder builder = new TransactionBuilder();
                    TransactionBuilder builder = Network.Main.CreateTransactionBuilder();


                    builder.AddKeys(secret);
                    builder.AddCoins(coins);
                    builder.Send(BitcoinAddress.Create(toAddress, Network.Main), Money.Satoshis(satoshisToSend));

                    // Calculate fee (fixed fee for simplicity)
                    Money fee = Money.Satoshis(10000); // 0.0001 BTC
                    builder.SendFees(fee);

                    // Set change address
                    builder.SetChange(secret.GetAddress(ScriptPubKeyType.Legacy));

                    // Build and sign the transaction
                    Transaction tx = builder.BuildTransaction(true);

                    // Verify the transaction
                    bool verified = builder.Verify(tx);
                    if (!verified)
                    {
                        Console.WriteLine("Transaction verification failed.");
                        return null;
                    }

                    // Serialize transaction
                    string rawTx = tx.ToHex();

                    // Broadcast transaction
                    string broadcastUrl = "https://api.blockcypher.com/v1/btc/main/txs/push";
                    var content = new StringContent($"{{\"tx\": \"{rawTx}\"}}", Encoding.UTF8, "application/json");
                    var broadcastResponse = await client.PostAsync(broadcastUrl, content);
                    if (!broadcastResponse.IsSuccessStatusCode)
                    {
                        Console.WriteLine("Error broadcasting transaction.");
                        var errorContent = await broadcastResponse.Content.ReadAsStringAsync();
                        Console.WriteLine($"Error details: {errorContent}");
                        return null;
                    }

                    var broadcastJson = await broadcastResponse.Content.ReadAsStringAsync();
                    dynamic broadcastData = JObject.Parse(broadcastJson);
                    string txHash = broadcastData.tx.hash;
                    return txHash;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Exception occurred: {ex.Message}");
                    return null;
                }
            }
        }
    }
}
