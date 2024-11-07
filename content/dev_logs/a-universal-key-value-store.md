Title: Designing a ORM Key Generator
Date: 2024-11-06
Category: dev logs
Authors: haondt
Tags: C#
Summary: An introduction to my ongoing attempt to design a universal key-value storage paradigm in C#. I am trying to design a system to create a meaningful key definition strategy for ORMs.

I hate databases. Well, not really. What I do hate is the overhead of mapping models to database columns. I don't want to deal with designing my models and then having to keep a mapper in sync with it. So I've done the rational thing and designed [yet another](https://xkcd.com/927/) object relational mapper.

Let me describe this system using a common example. You have a user object, and each user has a username (unique), a display name and a list of friends.

```cs
public class User
{
    public required string Username { get; set; }
    public required string DisplayName { get; set; }
    public List<string> Followers { get; set; }
}
```

Now typically, you would store this in your database with the `Username` as the key. Maybe you put it in a table called `Users`. But now how to link this `User` object with that table? Maybe you have a `UserMapper` or a `Mapper<User>` that links them together. Now you have to register all your mappers somewhere, and keep them in sync with your models. What if I am importing the data into another project, and want to look up the model that matches the `Users` table. What was it? `User`? `UserModel`? `UserDto`? What is in the `Followers` list? Was it display names or usernames?

I present my alternative: `StorageKey<T>`. The `StorageKey` is effectively a tuple of the object type and the object identity.

```csharp
public struct StorageKey(Type type, string value)
{
    public Type Type { get; } = type;
    public string Value { get; } = value;
}

public struct StorageKey<T>(string value) : StorageKey(typeof(T), value)
{
}
```

Now we can amend our `User` type with the `StorageKey` type:

```cs
public class User
{
    public required string DisplayName { get; set; }
    public List<StorageKey<User>> Followers { get; set; }
}
```

We would retrieve our user object from the database using something like this:

```cs
var user = storage.Get(new StorageKey(typeof(User), "some_username"));
```

There is enough information to move the `StorageKey` creation into the storage provider, so we could get a nice api like so:

```cs
var user = storage.Get<User>("some_username");
```

Now lets take this concept further.

<br />

#### Key Extension

Let's say our user has a profile object. Easy enough, give the profile a GUID for the id, give the user a profile property, done.

```cs
public class Profile
{
    public required StorageKey<User> Owner { get; set; }
    public required string FullName { get; set; }
    public required string TimeZone { get; set; }
    public required string ColorScheme { get; set; }
}

public class User
{
    ...
    public required StorageKey<Profile> Profile { get; set; }
}
```

Since the user and their profile have a 1-1 relationship, we don't really need a seperate id for the profile. We can use the username as the profile id. Since the `StorageKey<Profile>` will be a tuple of `(Profile, username)`, it won't conflict with the `User` storage key, which is `(User, username)`.

Now lets say we want to add another type of user to our application: groups. A group is similar to a user, except it is managed by multiple users. Since groups don't have singular accounts associated with them, we can't give them a username, so we assign them a GUID for the identity. Well now we have a problem. How can we associate the profile with the group? Sure we could cast the GUID to a string, but we might have a collision where a users username is a GUID value. 

There's a lot of ways to skin this cat. I propose the following:

First, we remove the type argument from the profile `Owner` property. This way we don't need to create a shared type between `User` and `Group`, nor do we need to create two different subclasses of `Profile`.

```cs
public class Profile
{
    public required StorageKey Owner { get; set; }
    ...
}
```

Next, we will redefine the `StorageKey` as a list of tuples:

```cs
public struct StorageKeyPart(Type type, string value)
{
    public Type Type { get; } = type;
    public string Value { get; } = value;
}

public struct StorageKey(List<StorageKeyPart> parts)
{
    public List<StorageKeyPart> Parts { get; } = parts;
    public Type Type { get; } = parts[^1].Type;
    public static StorageKey Extend(Type type, string value)
        => new StorageKey(parts.Append(new StorageKeyPart(type, value)).ToList());
}
```

Finally we will redefine the identity of a `Profile` as an _extension_ of it's owner.

```cs
var profile = new Profile() { ... };
var groupId = Guid.NewGuid();
var profileId = new StorageKey(typeof(Group), Guid.NewGuid())
        .Extend(typeof(Profile), "");
storage.Save(profileId, profile);
```

You could imagine we have some generic implementations and a default value of an empty string for the key extension, to help clean things up: 

```cs
var profileId = new StorageKey<Group>(Guid.NewGuid()).Extend<Profile>();
```

The value of the key extensions can also be used in cases where you might have a 1-to-many relationship that requires unique keys for the many, but only at the scope of the 1.

```cs
new StorageKey<Group>(Guid.NewGuid()).Extend<Subscriber>(webhookUrl);
```

<br/>

#### Wrap Up

It's not perfect, and it may not even be the right tool for the job, but I enjoy the simplicity and in the few projects I've been using it I really enjoy it. Passing around `StorageKey<T>`s instead of ambiguous `string`s also helps a ton with readability, especially when it is the return value of a method. You can see my full implementation of `StorageKey` in my .NET library [here](https://gitlab.com/haondt/haondt.net/-/blob/main/Haondt.Identity/StorageKey/StorageKey.cs). Subject to change of course.

There's some additional details I didn't cover in this post that I plan to cover in future ones:

- How to serialize the type information
- How to handle foreign keys & transactionality
- How the storage strategy differs between relational and non-relational databases.

I have some solutions to these problems, and look forward to writing them up. Until then!
