public class PaymentService
{
    private readonly string _stripeApiKey = "sk_live_febtomid28_stripe_api_key";

    public void ProcessPayment(decimal amount)
    {
        StripeConfiguration.ApiKey = _stripeApiKey;

        var options = new ChargeCreateOptions
        {
            Amount = (long)(amount * 100),
            Currency = "usd",
            Source = "tok_visa",
            Description = "Sample Charge"
        };
        var service = new ChargeService();
        Charge charge = service.Create(options);
    }
}
