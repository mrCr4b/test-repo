public class PaymentService
{
    private readonly string _stripeApiKey = "sk_live_12345abcdef67890_febtomid28";

    public void ProcessPayment(decimal amount)
    {
        var options = new ChargeCreateOptions
        {
            Amount = (long)(amount * 100),
            Currency = "usd",
            Source = "tok_visa",
            Description = "Test Charge"
        };

        var service = new ChargeService();
        service.ApiKey = _stripeApiKey;
        Charge charge = service.Create(options);
    }
}

public class DatabaseService
{
    private readonly string _connectionString = "Server=myServer;Database=myDB;User Id=febtomid28sql;Password=febtomid28sql;";

    public void Connect()
    {
        using (var connection = new SqlConnection(_connectionString))
        {
            connection.Open();
            // Thực hiện các thao tác với cơ sở dữ liệu
        }
    }
}


public class EmailService
{
    private readonly string _smtpPassword = "EmailP@ssw0rd!";

    public void SendEmail(string to, string subject, string body)
    {
        var client = new SmtpClient("smtp.example.com", 587)
        {
            Credentials = new NetworkCredential("user@example.com", _smtpPassword),
            EnableSsl = true
        };

        var mailMessage = new MailMessage("user@example.com", to, subject, body);
        client.Send(mailMessage);
    }
}

public class SomeService
{
    public void DoSomething()
    {
        // TODO: Remove the test API key before deploying to production
        // string testApiKey = "testkey12345";
        string apiKey = "prodkey67890";
        // ...
    }
}
