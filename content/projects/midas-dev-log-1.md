Title: Midas Dev Log #1
Date: 2025-02-10
Category: projects
Authors: haondt
Slug: midas-dev-log-1
Tags: C#, htmx
Summary: Exploring some of the updates, improvements and fixes I made to _Midas_ since my introductory post.

In my [previous post](/midas.html), I introduced [Midas](https://github.com/haondt/midas), a budgeting tool I designed since I couldn't find any other that matches my exact budgeting style. At the time of the post, I had "finished" the project in that it was in a somewhat usable state. After using it for all of maybe 10 minutes, I found myself with a list of bugs, improvements and changes I wanted to make. After fixing it, I'd find more things I wanted to improve. This repeated for about 3 weeks before tapering off, so I thought I'd write this post to showcase those changes.

I'll skip over the bugfixes and minor tweaks, focusing instead on the interesting bits.

<br />

[TOC]

<br />

### Supercategories

I initially built Midas with two options for indexing transactions - Categories and Tags. Transactions required exactly one of the former and could have zero or more of the latter. This way you have both an opt-in and a required way of sorting them. The issue was that when it comes to reports, I need to know where every cent is going, so I only really looked at categories. 

Categories are a good way to see where the money is going every month - how much is spent on groceries, on rent, on toys etc. But at the same time, I also needed to know flat-out how much is going to needs, and how much is going to wants. So I decided to add a second level of categorization: Supercategories.

[responsive-images](/images/midas-dev-log-1/supercategories.png|Supercategories)

Every category belongs to exactly one supercategory, and the report has metrics partitioned by category, and by supercategory.

<br />

### Split & Merge

Midas already has a "reconcile" feature that will automatically combine transactions. Given a transaction of `x$` from account 1 to account 2, and another transaction of `x$` from account 2 to account 3, we can safely combine both transactions into a single transaction of `x$` from account 1 to account 3, without changing any balances.

I found out in some cases, when I make two transfers in quick succession between certain banks, one bank reports one transfer of `x$` and one transfer of `y$`, while the other bank reports a single transfer of `(x + y)$`. The reconcile tool can't handle this (and I have no interest in trying to support it), so I instead added a way to manually "force" merge 2 _or more_ transactions. 

[responsive-images](/images/midas-dev-log-1/merge.png|Merge|large)

Equivalently, I have a few use cases for splitting a transaction into many:

- You could imagine in the above scenario I could have instead split the `(x + y)$` transfer into two transactions, then let the reconcile merge them together
- Splitting a purchase at the supermarket into groceries and some "fun spending" done at the same time 
- Un-merging a merged or reconciled transaction

So I added a split feature as well.

[responsive-images](/images/midas-dev-log-1/split-1.png,/images/midas-dev-log-1/split-2.png|Split source transaction,Split new transactions)

<br />

### Click to View

In many sections of the report, I would have a table row for a certain grouping of transactions, along with a metric. "Cash flow per account", "Spending per category", etc.

[responsive-images](/images/midas-dev-log-1/old-report.png,|A section of the report)

If I saw this and wanted to drill down (e.g. "what _exactly_ was I buying in this category?"), I would have to go to the transaction search and manually set up some filters to find the transactions corresponding with that table row. So instead I hyperlinked basically everything so that you can click on the grouping and it will pop up a list of all the transactions that are contributing to it.

[responsive-images](/images/midas-dev-log-1/click-to-view-1.png,/images/midas-dev-log-1/click-to-view-2.png|Supercategorical spending section of report,Transaction list modal|small)

<br />

### Report updates

On the subject of the report, I also made some changes there. Previously I had a section for a table of the spending per category, and a bar chart for the spending per supercategory. I like the bar chart because it conveys the information visually, but I need the table so I can hyperlink it to the transaction list modal. So I wanted both for the categories and the supercategories. On top of this, I also wanted a chart showing the spending for each as a percentage of total spending and of total income. This is 8 total charts to add to the report, which was starting to make things feel a little sprawley.

I needed a way to group them together. Essentially I wanted tabs, so I could have a single section dedicated to categories for example, and the tabs would map to all the different ways of breaking it down. I played around with a bunch of different [Bulma](https://bulma.io/) elements until I found something I liked.

[responsive-images](/images/midas-dev-log-1/report-update-1.png,/images/midas-dev-log-1/report-update-2.png|Percentage of Spending,Bar chart)

<br />

### Embedded Node-RED Editor

Despite being the smallest change here, this is by far my favorite. I simply added a page that contains an `iframe` pointing at the Node-RED editor. The convenience here is huge. Often I want to open the flows in one Chrome window and have Midas open in another for debugging. Previously, I'd have to open a new tab, recall the url for the Node-RED instance, and type it in. Now I just middle-mouse-click the link in the menu and I'm there. I only need to bookmark a single url and the application feels more cohesive.

[responsive-images](/images/midas-dev-log-1/editor.png|Embedded editor)

That about wraps it up for the changes I wanted to go over. Like I said before, there were some bugfixes as well, and other minor improvements. Despite all this, the [todo list](https://gitlab.com/haondt/midas/-/blob/5697ffdda675eeb8c67f67bfd75dd0a6ecd08075/docs/todo.md) is much, much longer than it was before, so perhaps there will be another post. I mentioned in the previous post that I was considering reworking the persistence layer. I recently finished rebuilding another project, [GSM](https://gitlab.com/haondt/gabbro-secret-manager). I took that rebuild as an opportunity to try out [EF Core](https://learn.microsoft.com/en-us/ef/core/), and found it to be a really good fit. I think it would fit well in Midas too, as it would reduce the code a bit and provides a solution for db migration.
