---
layout: post
title:  Design Better URLs
date:   2020-09-17 14:01:01 +0600
categories: [Backend]
tags: [REST, API, URL Design]
---
If you are designing RESTful APIs, designing the URLs is always a challenge. In this post, I tried to summarize a few key points that might help you to design better URLs.


### URL Root Prefix

Always specify a root prefix for your RESTful project. Whether it can be a generic word like `api`, `rest`, or `service` really depends on the domain. If the domain is already self-explanatory — say `api.tardy.com`, or a dedicated `tardy.com` — then a generic `/api` prefix (or none at all) is perfectly fine. But when several services share a single host or domain, prefer a single ASCII lowercase word tied to the project, so each stays distinguishable. For example `/tardy`, `/panacea`, etc. If you must use multiple words, separate them with a dash (`-`), for example `/tardy-api`.

A root prefix is helpful because it can be used with load balancers like HAProxy, or for URL redirection when there are multiple deployments on one machine.


### API Major Version

Although optional, the API major version should be the 2nd segment of RESTful URLs. For example, `/tardy/v1`.

A major version segment allows us to deploy multiple versions of the API over the same IP and port, while keeping backward compatibility.

That said, putting the version in the URL is a debated choice. Some argue the version doesn't belong in the URI at all and prefer header- or media-type-based versioning (for example, through the `Accept` header), or evolving the API without breaking changes. Path versioning is the pragmatic, widely-used option, but it's worth knowing the alternatives exist.

For example, media-type versioning moves the version into the `Accept` header, leaving the path version-free:

    GET /tardy/config
    Accept: application/vnd.tardy.v1+json


### Resource Paths

The following segments should be designed to describe a resource or service as clearly as possible. It is preferable to use different HTTP verbs such as `GET`, `PUT`, `POST`, `DELETE`, `PATCH` and `HEAD`, based on their recommended uses, especially if it allows us to reduce the number of different URLs. [Here’s a short read about some of these methods](https://www.restapitutorial.com/lessons/httpmethods.html).

For example, instead of creating three URLs to find a resource, update it, or delete it, it is better to create one URL and use GET, PUT and DELETE verbs for the URL. It reduces verbosity and documentation overhead, and it makes better sense of HTTP verbs within the RESTful resource life-cycle.

| Bad                            | Good                                                |
| ------------------------------ | --------------------------------------------------- |
| [POST] /tardy/v1/create-config | [POST]   /tardy/v1/config → Creates a configuration |
| [POST] /tardy/v1/update-config | [PUT]    /tardy/v1/config → Updates a configuration |
| [POST] /tardy/v1/delete-config | [DELETE] /tardy/v1/config → Deletes a configuration |

Usually, the first segment of the resource path will be your controller name, or resource name. For example, `/tardy/v1/guest`. The following segments should contain some sort of identifier, or words that further describe the nature of the service or resource that cannot be sufficiently explained by the HTTP verbs used with the URL. For example, you may want to find all appointments of your guests; the URL could be `/tardy/v1/guest/{guest_id}/appointments`. Here `guest_id` is an identifier, which is likely to be the resource id of the guest object in question.


### Dynamic vs. Static

The previous example brings out an interesting point between dynamic and static segments. Here, `guest_id` is a dynamic parameter as it is likely to change among requests. On the other hand, `appointments` is a static segment, it is pre-defined by your source code. It is HIGHLY encouraged that you do not use dynamic and static segments at the same position with the same preceding segments, because you never know if someone created an identifier that was the same as your predefined segment, and then your request router will become very confused.

Will your code ever put a check whether you won’t let someone create identifiers with specific keywords? The entire validation rule will seem very unnecessary and weird. Here’s an example:

| Bad                              | Good                               |
| -------------------------------- | ---------------------------------- |
| [GET]  /tardy/v1/guest/me        | [GET]  /tardy/v1/guest/me          |
| [GET]  /tardy/v1/guest/guest1001 | [GET]  /tardy/v1/guest/g/guest1001 |

Several popular online services use a pattern like this — LinkedIn's `/in/{profile}`, for instance — and for good reasons. It does not have to be a single letter, you can use whatever you want, as long as it remains meaningful.


### Avoid Consecutive Identifiers

Sometimes it is tempting to keep the URLs very short. But this often makes them confusing. For example, if we wanted to find a specific appointment for a specific guest, we could create this resource URL: `/tardy/v1/guest/{guest_id}/{appointment_id}`. While it looks fine when you describe it like that, let’s look at an actual URL: `/tardy/v1/guest/1/2`. Now, who’s to say what was `1` and what was `2`? It is always better to precede every dynamic segment with a static one. It also helps us to create a separation that goes well with the suggestions from the previous section - “Dynamic vs. Static”. Instead, this is much cleaner: `/tardy/v1/guest/1/appointment/2`.


### Avoid Segments Exposing Session Data

If something can and should be sent via authentication tokens, or session data, that should not be a part of the resource URL. For example, an authenticated user wants to load their own appointments. We could design the URL as: `/tardy/v1/user/{user_id}/appointments`. However, you already know the `user_id` from request header. Furthermore, allowing consumers to specify an id may even open up vulnerabilities or undesired outcomes.

This could be designed simply as: `/tardy/v1/appointments`. Now, you can see we run into trouble: some of the appointment URLs look like `/tardy/v1/user/{user_id}/appointments`, while some others look like `/tardy/v1/appointments`. This is where your planning skills kick in. Either you can keep it as such, since there is no real issue here. Or you can move the user related segments around, for example, `/tardy/v1/appointments/user/{user_id}`. That way, if you wanted to load someone else’s appointments, the same controller service could be used.

| Bad                                         | Good                         |
| ------------------------------------------- | ---------------------------- |
| [GET] /tardy/v1/user/{user_id}/appointments | [GET] /tardy/v1/appointments |


### Acknowledge the Trailing Slash (`/`)

It is a common practice to ignore the trailing slash in the URLs. However, HTTP never specified that having a trailing slash or not having a trailing slash are same things. In fact, these are two different URLs: `/tardy/v1/guest` and `/tardy/v1/guest/`. While most frameworks will handle these for you, others like Python-Flask are more nuanced: a route declared with a trailing slash (`/tardy/v1/guest/`) redirects the slash-less form to it, but a route declared without one (`/tardy/v1/guest`) returns a 404 for the trailing-slash version instead of redirecting. It is a good practice to specify both explicitly if you want to allow both. It is even better to design URLs in a way that there is no trailing slash hanging out.

A common place where this occurs is when you define your URL prefix somewhere else in the code, and in your controller you add a route with only (`/`) without much thinking.


### Query Parameters

Usually optional parameters, light-weight dynamic parts, signature keys, data that needs to be encoded / decoded differently, or data that needs URL quote / unquote functionality should be part of query parameters, not the URL itself. For example, when listing a collection you often want optional filtering, sorting, and pagination. Those belong in the query string, not the path:

    GET /tardy/v1/guest?status=active&sort=-created_at&page=2&limit=20

Here `status`, `sort`, `page`, and `limit` are all optional and freely combinable. Turning them into path segments would multiply your routes and force the controller to handle every combination, whereas a query string keeps a single, clean endpoint.


### Conclusion

These are merely suggestions and practices followed by many well-established products. There are always exceptions and special cases. Developer discretion advised.
