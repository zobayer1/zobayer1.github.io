---
layout: post
title:  Design Better URLs
date:   2020-09-17 14:01:01 +0600
categories: published restful design api
---
If you are designing RESTful APIs, designing the URLs is always a challenge. In this post, I tried to summarize a few key points that might help you to design better URLs.


### URL Root Prefix

Always specify a root prefix for your RESTful project, and it should not be generic words like `api`, `rest`, `service` etc. It should be a single ASCII lowercase word related to your project. For example `/tardy`, `/panacea` etc. If you must use multiple words, separate them with a dash (`-`). For example, `/tardy-api`.

A root prefix is important because this can be used with load balancers like HA-Proxy, or URL redirection when there are multiple deployments in one machine.


### API Major Version

Although optional, but the API major version should be the 2nd segment of RESTful URLs. For example, `/tardy/v1`.

A major version segment allows us to be able to deploy multiple versions of API over same IP and Port, while keeping a backward compatibility.


### Resource Paths

The following segments should be designed to describe a resource or service as clearly as possible. It is preferable to use different HTTP verbs such as `GET`, `PUT`, `POST`, `DELETE`, `PATCH` and `HEAD`, based on their recommended uses, especially if it allows us to reduce the number of different URLs. [Here’s a short read about some of these methods](https://www.restapitutorial.com/lessons/httpmethods.html).

For example, instead of creating three URLs to find a resource, update it, or delete it, it is better to create one URL and use GET, PUT and DELETE verbs for the URL. It helps to reduce verbosity, documentation overhead and it makes better sense out of HTTP verbs with RESTful resource life-cycle.

| Bad                            | Good                                                |
| ------------------------------ | --------------------------------------------------- |
| [POST] /tardy/v1/create-config | [POST]   /tardy/v1/config → Creates a configuration |
| [POST] /tardy/v1/update-config | [PUT]    /tardy/v1/config → Updates a configuration |
| [POST] /tardy/v1/delete-config | [DELETE] /tardy/v1/config → Deletes a configuration |

Usually, the first segment of resource path will be your controller name, or resource name. For example, `/tardy/v1/guest`. The following segments should contain some sort of identifiers, or words that further describes the nature of the service or resource which cannot be sufficiently explained by HTTP verbs used with the URL. For example, you may want to find all appointments of your guests, the URL could be `/tardy/v1/guest/{guest_id}/appointments`. Here `guest_id` is an identifier, which is likely to be the resource id of the guest object in question.


### Dynamic vs. Static

The previous example brings out an interesting point between dynamic and static segments. Here, `guest_id` is a dynamic parameter as it is likely to change among requests. On the other hand, `appointments` is a static segment, it is pre-defined by your source code. It is HIGHLY encouraged that you do not use dynamic and static segments at the same position having same preceding segments. Because, you never know if someone created an identifier that was same as your predefined segment, and then your request router will become very confused.

Will your code ever put a check whether you won’t let someone to create identifiers with specific keywords? The entire validation rule will seem very unnecessary and weird. Here’s an example:

| Bad                              | Good                               |
| -------------------------------- | ---------------------------------- |
| [POST] /tardy/v1/guest/create    | [POST] /tardy/v1/guest/create      |
| [GET]  /tardy/v1/guest/guest1001 | [GET]  /tardy/v1/guest/g/guest1001 |

If you look at popular online services like Gmail, Messenger, LinkedIn, Twitter etc, they all follow this pattern, and for good reasons. It does not have to be a single letter, you can use whatever you want, as long as it remains meaningful.


### Avoid Consecutive Identifiers

Sometimes it is tempting to keep the URLs very short. But this often makes them confusing. For example, if we wanted to find a specific appointment for a specific guest, we could create this resource URL: `/tardy/v1/guest/{guest_id}/{appointment_id}`. While it looks fine when you describe it like that, let’s look at an actual URL: `/tardy/v1/guest/1/2`. Now, who’s to say what was `1` and what was `2`? It is always better to precede every dynamic segment with a static one. It also helps us to create a separation that goes well with the suggestions from previous section - “Dynamic vs. Static”. Instead, this is much cleaner: `/tardy/v1/guest/1/appointment/2`.


### Avoid Segments Exposing Session Data

If something can and should be sent via authentication tokens, or session data, that should not be a part of the resource URL. For example, an authenticated user wanted to load his own appointments. We could design the URL as: `/tardy/v1/user/{user_id}/appointments`. However, you already know the `user_id` from request header. Furthermore, allowing consumers to specify an id may even open up vulnerabilities or undesired outcomes.

This could be designed simply as: `/tardy/v1/appointments`. Now, you can see we run into a trouble, some of the appointment URLs look like `/tardy/v1/user/{user_id}/appointments`, while some others look like `/tardy/v1/appointments`. This is where your planning skills kick in. Either you can keep it as such, since there is no real issue here. Or you can move the user related segments around, for example, `/tardy/v1/appointments/user/{user_id}`. That way, if you wanted to load someone else’s appointments, the same controller service could be used.


### Acknowledge the Trailing Slash (`/`)

It is a common practice to ignore the trailing slash in the URLs. However, HTTP never specified that having a trailing slash or not having a trailing slash are same things. In fact, these are two different URLs: `/tardy/v1/guest` and `/tardy/v1/guest/`. While most frameworks will handle these for you, there are others like “Python-Flask” who do not perform this automatic redirection. It is a good practice to specify both explicitly if you want to allow both. It is even better to design URLs in a way that there is no trailing slash hanging out.

A common place where this occurs is when you define your URL prefix somewhere else in the code, and in your controller you add a routing with only (`/`) without much thinking.


### Query Parameters

Usually optional parameters, light-weight dynamic parts, signature keys, data that needed to be encoded / decoded differently, or data that needed URL quote / unquote functionalities should be part of query parameters, not the URL itself. Here’s an example of an S3 object’s URL generated by CloudFront.


    https://getboing.panaceahealth.ai/53631c95-aa43-4e94-9e3f-e2571bb80a69/1600096846387.png?Expires=1600865053&Signature=jXMGGLGhBPZwpC-fkXWqcXZa18AGQqK0yO~3o~kQLDOS2nlY7ZDUAh4jKB2oucvHkonY0E4oIRnVVlg3gYh63a4UPKNmssDOLGsvDDKZH5vwYqNa~78Ys3xBBwYyXzJRhVOX-MYN0KIlwoEnz0xDbBiNV8mbJsP5INIAcTZM3TW6kuYfRUb28PXHcm9lbtgLzNnMlP9KnfxVkjMMhE4UWIC-pjctsgkhha6tp-KOHvSpNRJ5IjUm6C-Js1S66SybHIcDpntWm7dPWWOB1juxnjKR0WswAyNUJjPfeKHepBP89Fz9aQEkJZqFaJX-aNvrJ-Y0gH2rawx3u3PTxJ2ICw__&Key-Pair-Id=ODHELCJEYSLAEPWCJTQP

There are a lot of query parameters in this URL, and making them URL segments would mean that your controller methods would be receiving tons of parameters which would not give it a very clean look.


### Conclusion

These are merely suggestions and practices followed by many well established products. There are always exceptions and special cases. Developer discretion advised.
