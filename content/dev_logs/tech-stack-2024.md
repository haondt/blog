Title: My Tech Stack (2024)
Date: 2024-11-05
Category: dev logs
Authors: haondt
Slug: techstack-2024

### Web

#### Content

I've really been enjoying [htmx](https://htmx.org/). Really what I like is the underlying [HATEOAS](https://htmx.org/essays/hateoas/) principle that it enables. The way I see it, this allows the browser to become the frontend engine, and I no longer need a seperate process for serving the frontend, which is a huge boon. It's also much easier to debug, as I can just watch the network tab in the dev console and read the html that is coming from the server.

So at the core of all my web applications is htmx. For smaller sites I've been pairing it with [Flask](https://flask.palletsprojects.com/). At the time of writing, my main site, [haondt.dev](https://haondt.dev) is powered by just Flask and htmx. Due to all the time I've spent building my [automation pipelines](https://gitlab.com/haondt/pipelines) I've gotten pretty well versed in jinja2 templating, so it's been a fairly smooth experience building html templates.

For larger, more complex projects, like [elysium](https://gitlab.com/haondt/elysium), I've been building a component framework on top of Razor Pages and htmx. This framework is currently part of my personal .NET library [Haondt.Net](https://gitlab.com/haondt/haondt.net). The main feature of this component framework is tying a model to an html snippet. Similar to regular Razor Pages, you define an html snippet and a model.

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
    public string InviteLink { get; set; } = "";
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
    [HttpGet("generateInviteComponent")]
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



#### Styling

#### Scripting

### IDE

### Development Tools
