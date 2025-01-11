Title: Building My Perfect Budgeting Tool
Date: 2025-01-09
Category: projects
Authors: haondt
Slug: midas
Tags: C#, htmx
Summary: How (and why) I built _Midas_, a budgeting app perfectly suited to my personal finance management style.

Like many, when I first decided I needed to start budgeting my money, my first move was to load up a generic budget template in Google Sheets. By the time I had opened 3 or 4 bank accounts, updating the sheet had become extremely tedious. Reading through all my transactions, adding up the numbers, trying to make sure I didn't miss anything. It was time for me to graduate to something more powerful.

<br />

[TOC]

<br />

### Firefly III

Always looking for something else to host on [my home server](https://gitlab.com/haondt/gabbro), I settled on [Firefly-III](https://github.com/firefly-iii/firefly-iii), a lovely PHP app written by the absolute legend [James Cole](https://github.com/JC5). Firefly III was a huge improvement on my spreadsheet. The [double entry](https://en.wikipedia.org/wiki/Double-entry_bookkeeping) bookkeeping system combined with the seperate [data importer](https://github.com/firefly-iii/data-importer/) essentially eliminated the potential of entering transactions incorrectly, and it had substantially better UX as compared to a couple spreadsheets.

[responsive-images](/images/midas/firefly-iii.png|Firefly III)

But there was still room to improve. At the top of the list was the rule system. When you import your transactions using the data importer, it can set either the source or the destination account, but not both. This is because the importer knows the one account being imported against, and it knows whether it is a deposit or withdrawal, but it can't determine the _opposing_ account.

This is where the rule system comes in. A rule can update any part of a transaction (source/destination account, category, tags, etc) based on any other part. Great! I can create rules to set the opposing account by parsing the transaction description. Herein lies the issue. The available tools are simply not powerful enough.

- The available comparators, `starts with`, `ends with`, `equals`, `contains` and the complement (`not`) of each, are not enough to determine the account name from the description. Regular expressions alone would fix this issue, but the author has [explicitly refused](https://github.com/firefly-iii/firefly-iii/issues/1281) to implement them.
- The available combinators are too restrictive. You can effectively `AND` or `OR` all the rules together. I would like to at least nest comparisons.
- The available actions are too limited. You can only set the opposing account with a hardcoded string, meaning you have to create at least one rule for every possible account. Due to the above limitations though, you generally have to create multiple rules for each account.

[responsive-images](/images/midas/firefly-iii-rules.png|Firefly III rule configuration)

<br>

### The Post-Processor

Enter [Firefly-III-PP](https://github.com/haondt/firefly-iii-pp). This is a tool I built that leverages the Firefly III [API](https://docs.firefly-iii.org/how-to/firefly-iii/features/api/) to pull transactions from Firefly III, run them through a [Node-Red](https://nodered.org/) flow and use the result to update them. It has a couple extra features as described in the GitHub link above, but the Node-Red tie-in is the star of the show here.


[responsive-images](/images/midas/firefly-iii-pp.png|Firefly-III-PP|large)

With the postprocessor add-on, my rules could do anything, but there was still one avenue of improvement left: convenience. With my current setup, I had to run 5 seperate docker containers:

- Firefly III
- MariaDB
- Data Importer
- Post-Processor
- Node-Red

Due to the way it was designed, I had to run the post-processor and Node-Red flow locally, and the other containers on my server. Any time I had to recreate anything I'd have to go in and reconfigure the api keys, accounts, etc. To "open" it, I had to launch Docker Desktop, then start the containers, then open them in my browser. It was kind of a pain to maintain and use such a fragmented system.

Furthermore, Firefly III simply has too many features. I don't need multiple users, bills, piggy banks, recurring transactions, etc. I have a pretty basic budgeting philosophy (see below), and just need what is effectively a hosted spreadsheet with some automation.

So I wanted something that was more cohesive, and something with fewer features.

<br>

### Midas

[Midas](https://github.com/haondt/midas) is the result of taking the postprocessor to its logical conclusion. I used Sqlite for persistence, integrated the importer and made it a two-stage process that runs the csv through Node-Red, allows the user to review the result, and finally persists it in storage. 

[responsive-images](/images/midas/import.png,/images/midas/dry-run.png|Transaction import,Import confirmation)

Beyond the transaction import, Midas more or less reaches feature parity with the postprocessor, and matches all the features from Firefly III I find to be useful. The data importing currently only supports csv, as I have security concerns with systems like [Plaid](https://plaid.com/). [Open Banking](https://www.canada.ca/en/financial-consumer-agency/services/banking/open-banking.html) in Canada is in the works, and I plan to add support for it if and when the day ever comes.

[responsive-images](/images/midas/midas.png|Midas dashboard)

<br>

### Budgeting Philosophies

There are a lot of ways to think of a budget - envelope-based, zero-based, thinking in terms of assets and liabilities, debts, investments, etc. In my (humble) opinion, it doesn't need to be so complicated.

My philosophy on budgeting can be summarized in four pillars:

- minimize needs
- maximize income
- fixed ceiling on wants
- fixed floor on savings

Under this pretense budgeting becomes a three step process.

1. Do everything you can to reduce spending on "needs" as much as possible. At the same time, do everything you can to grow your income.
2. After a couple months of this, take your income minus your needs to see what you have to work with. Slice out a piece of that (% or $ amount) and consider it saved.
3. What's left can be spent freely.

Midas is built to enable this kind of budgeting. Categorization and report generation allows you to determine where money is going for steps 1 and 2.

[responsive-images](/images/midas/report.png,|A section of the report)

For step 3 all you have to do is open the app and check your total income minus your total spending ("Cash Flow" on the dashboard). If this amount is greater than your savings goal, you can spend more. If this amount is less than your savings goal, you are spending too much.

<br>

### Periodization

I generally break everything down month to month. Nothing in life really follows a strict schedule 100% of the time. Paycheques can be bi-weekly, semi-monthly, monthly or otherwise unpredictable. Expenses can vary significantly, one month I might fill up my car 4 times, the next month maybe not at all. 

Ultimately I just need to pick a time unit to reason with, and a month seems pretty good. If a month has something very irregular (restocking something I only buy every few months, yearly recurring expenses, etc) then I might look at a number of months or years as the period. Midas allows you to select any period for both the dashboard and the reports, but defaults to month-to-month.

<br>

### Flexibility

Earlier I said I felt Firefly III had too many [features](https://docs.firefly-iii.org/explanation/firefly-iii/about/introduction/). Midas intentionally has very simple "units".

- 2 Types of accounts: those included in your net worth, and those not.
- 1 Type of transaction: from one account into another. There is no distinction between withdrawals, deposits and transfers.
- No goals, budgets (ironic, I know), limits, or recurring transactions 

This is because, at the end of the day, things vary. My paychecks aren't always the same amount, my bills aren't always the same amount, sometimes I have a sudden expense or a sudden injection of cash. All I really care about is that my net worth is trending upwards, ideally at the rate of at least 1x my savings goal / period. So most of the metrics in Midas are based around balance deltas rather than actual amounts.

<br>

### The Tech Stack

Midas was an opportunity for me to figure out a couple different technologies I've been wanting to learn. First off, I took this as an opportunity to migrate [my web nuget](https://gitlab.com/haondt/haondt.net/-/tree/main/Haondt.Web.Core) from [Razor](https://learn.microsoft.com/en-us/aspnet/core/razor-pages/) to [Blazor](https://learn.microsoft.com/en-us/aspnet/core/blazor/). Oddly enough this made a large part of my web framework obselete, which cut down a lot on code. As opposed to my somewhat complicated [previous setup](/techstack-2024.html), I can simply build my Razor (Blazor) component, 

```razor
@code {
    [Parameter, EditorRequired]
    public required string InviteLink { get; set; }
}

<div class="field" style="width:100%;">
  <div class="control">
    <input 
        class="input"
        type="text"
        placeholder="Click &quot;Generate&quot; to generate a new link"
        value="@(!string.IsNullOrEmpty(Model.InviteLink) ? @Model.InviteLink : "")"
    >
  </div>
</div>
```

and immediately render it. No messing around with the service collection!


```csharp
[Route("admin")]
public class AdminController(IComponentFactory componentFactory, IAdminService adminService)
{
    [HttpGet("generate-invite-component")]
    public async Task<IResult> GetGenerateInviteComponent()
    {
        return await componentFactory.RenderComponentAsync(new GenerateInviteModel
        {
            InviteLink = await adminService.GenerateInviteLinkAsync();
        });
    }
}
```

This is possible due to the [`RazorComponentResult`](https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.http.httpresults.razorcomponentresult) introduced in .NET 8. Now it's [not perfect](https://github.com/dotnet/aspnetcore/issues/51923), and there are some [issues](https://github.com/dotnet/razor/issues/7349) with the `.razor` editing experience, but overall this setup is very clean compared to what I was doing before. Perhaps I'll do a seperate post on my experience with it in the future. 

I went with my standard [htmx](https://htmx.org/) + [hyperscript](https://hyperscript.org/) for interactivity on the frontend, with [Bulma](https://bulma.io/) for the styling. The same setup I've been playing with in another project, [Elysium](https://gitlab.com/haondt/elysium).

For the charts I initially wanted something non-js-based, and gave [Charts.css](https://chartscss.org/) a solid effort, but ultimately I didn't like the way they looked. I looked around at a few different Blazor frameworks, but they are all essentially a C# wrapper around a javascript framework. I didn't want to add a whole nuget for just that, in the end I decided to go with [Chart.js](https://www.chartjs.org/). I struggled a bit finding a sensical way to intergate it into my app, since I wanted to describe my chart data in C#. This meant I had to inject a C# model into a javascript model into a hyperscript snippet into a Razor component into an htmx response. On some occasions I needed to inject a javascript function into that C# model first. I wound up with this monstrosity:

```razor
<!-- Chart.razor -->

@using Midas.UI.Models.Charts

@code{
    [Parameter, EditorRequired]
    public required ChartConfiguration Configuration { get; set; }
}

<div style="position:relative;width:100%;height:100%;">
  <canvas
      _="
        on load
            js(me)
                return new Chart(me, @Configuration);
            end
            set :chart to it
        end
        
        on htmx:beforeCleanupElement
            set chart to :chart
            js(chart)
                chart.destroy();
            end
        end
        "></canvas>
</div>

```

The `.ToString()` method of `ChartConfiguration` is just a call to [`JsonConvert.SerializeObject`](https://www.newtonsoft.com/json/help/html/m_newtonsoft_json_jsonconvert_serializeobject.htm). There were some interesting challenges in getting this to work correctly. A sampling:

- Figuring out how to set up a callback on the [`htmx:beforeCleanupElement`](https://htmx.org/events/#htmx:beforeCleanupElement) event to ensure the chart object gets cleaned up.
- Figuring out what magic combination of css rules would play nice with Bulma [Columns](https://bulma.io/documentation/columns/basics/) and allow the chart to scale responsively.
- Writing a [discriminated union](https://en.wikipedia.org/wiki/Tagged_union) type, [`Union<T1, T2>`](https://gitlab.com/haondt/midas/-/blob/0a968a3426839923703a7559850938ba347c54d6/Midas/Midas.Core/Models/Union.cs). Interestingly, it seems like an "official" implementation is [coming soon](https://github.com/dotnet/csharplang/blob/18a527bcc1f0bdaf542d8b9a189c50068615b439/proposals/TypeUnions.md).
- Setting up some custom json converters to allow serialization of my custom types like `Union<T1,T2>` and of javascript functions.

Lastly, all the persistence is done with Sqlite. I had to write a lot of custom storage implementations for this project, which has me rethinking my strategy in my persistence nuget. I may need to revisit it later.

<br>

### Closing Thoughts

Overall I'm pretty happy with what I've created here. I still have a [backlog](https://gitlab.com/haondt/midas/-/blob/0a968a3426839923703a7559850938ba347c54d6/docs/todo.md) of features I'd like to add, but as it is currently it's at least usable. I might rework my persistence layer at some point too. There's a lot of repeated code in there and I don't really have a solution for db migrations. I am pretty satisfied with the UI/UX though, and look forward to putting it to use.
