public void ConfigureServices(IServiceCollection services)
{
    services.AddAuthentication()
        .AddGoogle(options =>
        {
            options.ClientId = "febtomid28GoogleClientId";
            options.ClientSecret = "febtomid28GoogleClientSecret";
        })
        .AddFacebook(options =>
        {
            options.AppId = "febtomid28FacebookAppId";
            options.AppSecret = "febtomid28FacebookAppSecret";
        });
}

public void ConfigureServices(IServiceCollection services)
{
    var key = Encoding.ASCII.GetBytes("febtomid28SuperSecretJwtKey");

    services.AddAuthentication(x =>
    {
        x.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
        x.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
    })
    .AddJwtBearer(x =>
    {
        x.RequireHttpsMetadata = true;
        x.SaveToken = true;
        x.TokenValidationParameters = new TokenValidationParameters
        {
            IssuerSigningKey = new SymmetricSecurityKey(key),
            ValidateIssuerSigningKey = true,
            ValidateIssuer = false,
            ValidateAudience = false
        };
    });
}

public void ConfigureServices(IServiceCollection services)
{
    services.AddDataProtection()
        .ProtectKeysWithCertificate("thumbprint_of_certificate");
}

