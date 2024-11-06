Title: My Tech Stack (2024)
Date: 2024-11-05
Category: dev logs
Authors: haondt
Slug: techstack-2024
Summary: My tech stack has changed quite a bit from 2023, primarily with the addition of htmx in essentially all my web projects. I've also been writing a lot more Python, the ease of use makes it very appealing. That and C# have been my main languages this year. 

### The Web

I've really been enjoying [htmx](https://htmx.org/). Really what I like is the underlying [HATEOAS](https://htmx.org/essays/hateoas/) principle that it enables. The way I see it, this allows the browser to become the frontend engine, and I no longer need a seperate process for serving the frontend, which is a huge boon. It's also much easier to debug, as I can just watch the network tab in the dev console and read the html that is coming from the server.

So at the core of all my web applications is htmx. For smaller sites I've been pairing it with [Flask](https://flask.palletsprojects.com/). At the time of writing, my main site, [haondt.dev](https://haondt.dev), is powered by just Flask and htmx. Due to all the time I've spent building my [automation pipelines](https://gitlab.com/haondt/cicd/pipelines) I've gotten pretty well versed in jinja2 templating, so it's been a fairly smooth experience building html templates.

For larger, more complex projects, like [elysium](https://gitlab.com/haondt/elysium), I've been building a component framework on top of Razor Pages and htmx. This framework is currently part of [my personal .NET library](https://gitlab.com/haondt/haondt.net). The main feature of this component framework is tying a model to an html snippet. Similar to regular Razor Pages, you define an html snippet and a model.

```html
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

```cs
public class GenerateInviteModel : IComponentModel
{
    public required string InviteLink { get; set; };
}
```

Then the model and the path to the template must be registered in the service provider.

```cs
services.AddScoped(sp => new ComponentDescriptor<GenerateInviteModel>()
{
    ViewPath = "~/Components/Admin/GenerateInvite.cshtml"
});
```

Finally, whenever we need to render out this component, we can use the provided factory.

```cs
[Route("admin")]
public class AdminController(IComponentFactory componentFactory, IAdminService adminService)
{
    [HttpGet("generate-invite-component")]
    public async Task<IActionResult> GetGenerateInviteComponent()
    {
        IComponent component = await componentFactory.GetComponent<GenerateInviteModel>(new GenerateInviteModel
        {
            InviteLink = await adminService.GenerateInviteLinkAsync();
        });

        return component.CreateView(this);
    }
}
```

There are many overrides and many ways to inject headers and other services into the response, but effectively it allows you to define a component and then render it anywhere (from a controller, from a filter, from inside another component, etc). The methodology for initializing the component can also be defined (or overridden) from anywhere, and in most cases has full access to the service provider. So right when you define the component you can say "this is how this component is initialized, using xyz services". And if you want, you can override that when you call the `IComponentFactory`. It makes for a flexible framework that abstracts away a lot of the rendering code. 

For any client-side scripting, I've been using [hyperscript](https://hyperscript.org/). The syntax is a bit difficult to wrangle but it pairs really nicely with htmx. Throwing the behavior right on the element feels very at home with respect to HATEOAS.

<br/>

### The Editor

For my IDE, my [Neovim config](https://github.com/haondt/dotfiles/tree/master/gypsum/.config/nvim) has matured enough to the point where I feel comfortable replacing VS Code with it. In fact I use Neovim for everything except C#. I'm a bit afraid to let go of Visualy Studio as 1) Omnisharp still seems a bit lackluster and 2) the terminal based `dotnet` experience isn't as nice as using the UI. I am considering switching over though, as I find Visual studio itself has some issues:

- Code Search is quite slow compared to something like ripgrep
- Navigation with VsVim has some quirks, like needing a code window open before you can use commands
- Hot Reload works maybe 40% of the time, I've actually had a much better experience using `dotnet watch` in another window 

That's not to say Neovim is perfect, but when something doesn't work the way I want it to and I take a ["fine, I'll do it myself"](https://www.youtube.com/watch?v=EzWNBmjyv7Y) kind of attitude, I usually have a lot more success in Neovim.

<br/>

That about sums up my stack for this year. Going into 2025, I think I'll be keeping things mostly the same, though I do want to pick up a new language to replace C#. I've had a couple rows with the garbage collector and there's some functional paradigms I'd like to see implemented at the language level (result types, union types, better optional support than `Nullable<T>`, etc). Rust has always been in the back of my mind but I haven't taken the time to really learn it in a meaningful capacity. Maybe I'll give it a proper go next year.

