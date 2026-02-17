I need you to help me brainstorm, plan, and build a series of agents, skills, and workflows to help me achieve the research and due diligence for data center sites and procurement. For additional context, I'm the director of marketing at Data Canopy, a data infrastructure company. I've been tasked by Andrew, the executive vice president of sales, to help create a workflow or a chatbot or some form of automation to help us with our due diligence when we are researching potential sites to partner with for data centers.

In the past, we have brokers or people who reach out to us with potential data center sites. Sometimes they are ready to go; sometimes they are looking for us to partner with them for additional partners and investments. And then together we end up being the organization that provides the fulfillment for that data center, and we find the client to fill the data center.

But we often get stuck with packets and deals that we need to look through and vet and do a lot of due diligence to decide if this is an opportunity that's even worth entertaining or not. Sometimes we'll get down that pipeline and discover that maybe the power hasn't really been secured for that data center or the proper environmental rules and regulations for that site don't match what the people said about it. Sometimes we encounter the actual property owner might not be who they say they are, because sometimes people will find these opportunities, they want to jump in and then bring it to us, and they are essentially the middle person trying to flip it and do a quick turnaround to make some money.

So sometimes we need to research who the actual owners are of the land and of the building. We need to know if the location and the zoning is correct for data centers, water rights, environmental due diligence, etc.

What I'd like to do is build out a system, a thorough system with multiple agents that have the appropriate skills and appropriate access to research to do this due diligence. When we get an opportunity, I will supply you with all of the files that I get. And then this workflow would initiate that does all the research, goes out, finds everything that we can, and ultimately produces an executive summary that we can use to quickly know if this is a worthwhile opportunity, what some of the details are about the opportunity, and it'll just help us filter these deals because when they come through with the amount of information that we have, it's very time consuming to go through all of it.

So this workflow or this automation that we're building will speed that up. If I were to run these automations on my own, I would do them here through Claude Code. However, we might want to consider a scenario where our employees can upload all the documentation to maybe a URL and that triggers off the automation. But that would be down the road.

First, I want this to work flawlessly here in Cloud Code for me, and then we can entertain if it would make sense to have it work somewhere else. So below, I'm going to share with you all of the context that I have. You'll use that context to evaluate what we're trying to achieve and what would be the best way to approach this as a workflow for this project. I'll put relevant information inside of XML tags so that you can maintain context. And then I want you to answer or to ask me questions to help you to achieve what we're trying to achieve. 

Another item worth noting: when we receive an opportunity and they send us all of the files, it's not always the same files. One opportunity might have some files while a different opportunity has a different set of files. The terminology will sometimes be different, sometimes one might refer to connectivity, another one might be referring to power. 

So our executive summary needs to be consistent. It's always the same essential template, but know that the data being analyzed by the research agents will not always be consistent in its terminology. The agents need to be strong enough or smart enough to extract what needs to be extracted.

I'm thinking it would be a matter of maybe designing specific agents. One might be an agent that specializes in understanding the commercials (how much is the land and the power, etc.), another one for zoning, another one for water rights, etc. You'll see there are several things that need to be researched.

I have access to Firecrawl API and Tavali API and any other external resources that might be needed to achieve the research that we need to do. Let me know because I can secure any kind of API or external platform that might help us in this whole process.

And if you think of different ways to run the automation, I can come up with whatever we need to, whether that's Google drives or if I put all the files in one single drive and then I invoke the overall agent or the plugin, whatever it is, however we do it. We could use Dropbox if we need to and that triggers the automation or N8N. or PipeDream.

Think through the various scenarios and we'll brainstorm that together. Let's get started with this process. 

### XML tags:

<andrews_request> - This section contains the email request from Andrew stating what he would like to have in a final report (executive summary).

<meeting_transcript_1> - this is the transcript of a meeting that I had with Andrew, where we talked about this, and he mentioned what he's trying to achieve. The meeting has a lot of good context to help you understand what we're trying to do 

<meeting_transcript_2> - this is the transcript of another short follow-up meeting that I had with Andrew, just clarifying a few more things about what we're trying to achieve 

<executive_summary_example> - this section contains an example of one of the final reports that Andrew manually wrote after doing all of his due diligence on this exact data set that we're working with. This just gives you an idea of the type of information and how he is hoping to present this information in his final report.

This is missing several sections because he hasn't had the ability to do all the research thoroughly for all of the separate items that need to be researched, but this is an example of the direction we're trying to go in terms of the results of the research 

<example_files> - This contains a full list of the files we have for this particular opportunity. Other opportunities will have similar information, however it might be more or less files and more or less information in each file. The consistency of data and files is never the same for each opportunity.

<executive_summary_example> - this is an example of the executive summary that Andrew did on his own from this particular data set. It's not complete because it's a work in progress, but it shows you the kind of information he's trying to gather and the ultimate output he's trying to achieve.

The ultimate output is a document that helps us and all parties involved to know if this is an opportunity that we want to continue to pursue or not, and what the main details are of the opportunity. This document should make it easy for us and others to know if this is an opportunity to continue pursuing, what kind of opportunity it is, and/or if it's advisable to not get involved with the opportunity.

Most of what the agents need to research and analyze is the content and data found in the files. There are a few things that might be worth checking online for due diligence if possible. 

For example, verifying the address and maybe looking at public records to see the owner's name and see if that matches the information we have in the files. Maybe doing some research on zoning or any other thing that we might not be thinking of. 

The agents need to be experts in data center infrastructure and the data center industry in general 

### XML Context:

<example_files>

'/opportunity-example' (All files in this folder represent a data set of what we might see for any given opportunity. In this case, these are all the files we have for "Pioneer Park")

</example_files>

<executive_summary_example>

**Executive Summary — DataNovaX Pioneer Park**

**Location:** Airport Drive, Wichita Falls, TX **Project Type:** Phased data center campus

**Primary Use Case:** AI, regional hyperscale, and government-adjacent workloads

**Overview**

Pioneer Park is a credible, early-stage data center site suitable for phased development. Only the initial power tranche is fully executable today. The project should be underwritten as a 12 MW anchor with expansion optionality, not as a fully powered hyperscale campus at this stage.

**Power**

**Firm:** 12 MW of grid power via Oncor. Interconnection study completed with an executed FEA. No interconnection cost for the initial tranche. Target delivery: Q2 2026 (conservative).

**Planned:** Expansion to 40–50 MW dependent on on-site natural gas generation, EPC execution, and gas interconnection timing. Phase II (100+ MW) remains conceptual with no executed utility agreements.

**Fiber & Connectivity** 

Carrier-neutral site with 15+ identified carriers, including long-haul and metro fiber. Documented route diversity supports redundancy. Connectivity is strong for a secondary Texas market, though not equivalent to core DFW or Ashburn depth. 

**Water / Cooling**

Liquid-cooling-capable design with an 8.6 million gallon water agreement referenced. No evidence of water scarcity, moratorium risk, or contested rights. Confirmation of duration and transferability is recommended. 

**Land, Zoning & Entitlements**

Land acquisition completed with title secured. Civil engineering, drainage, grading, and trenching are complete. Pre-plan review has been completed and building permits have been initiated. Local jurisdiction engagement appears supportive for Phase I. 

**Key Risks**

Power scale beyond the initial 12 MW is not contractually secured. On-site generation introduces EPC and schedule coordination risk. Wichita Falls is a secondary market where hyperscale demand is likely

price-sensitive. 

**Bottom Line & Recommendation**

Phase I is real, buildable, and financeable. Expansion capacity should be treated as contingent upside. Base valuation on firm, contracted power only, with later MW re-rated upon execution of gas, EPC, and expanded utility agreements.

</executive_summary_example>



<andrews_request>

I want to be able to quickly do a level of diligence that will validate, via the data room docs, these things. 

1. Secured power. This is power that is contracted for and available at time of purchase. Not speculative.
2. Control- who owns the property today.  Entitlements
3. Zoning- is the site zoned for Data Center
4. Water Rights
5. Environmental Due Diligence (Natural disaster type stuff.
6. Commercials- how much is the land/power
7. Risks that we need to focus on
8. Natural gas availability 
9. Comparable in the market of previous sales

This would be an awesome start. 

</andrews_request>

### Additional Context

<meeting_transcript_1>

**Noah Rasheta | 00:01 
**Hey, Andrew. 
**Speaker 2 | 00:03 
**Hey, man, how are you? 
**Noah Rasheta | 00:04 
**Good. How are you? 
**Speaker 2 | 00:06 
**Good. I was just thinking about something. I started to work on something, but I bet you could probably help me with it. 
**Noah Rasheta | 00:12 
**Sure? 
**Speaker 2 | 00:13 
**So I started screwing around with ChatGPT to perform, like, a level of due diligence on, like, data rooms. 
And I was shocked at how quickly it did it. 
**Noah Rasheta | 00:28 
**Yeah, I do. 
**Speaker 2 | 00:29 
**But it needs tweaked a lot. And I know you can make, like, kind of your own GPTS for specific, you know, activities or have you done that before? So. 
**Noah Rasheta | 00:43 
**Really? Complex ones. 
**Speaker 2 | 00:46 
**Sweet. 
So I'm going to send you a list. Is it hard? I don't want it to take up too much time. 
**Noah Rasheta | 00:55 
**No, it's not. 
**Speaker 2 | 00:55 
**Like, okay, cool. So what I did is I took. I just took a data room that I got for one of these sites and I said, you know, these are the most important things, you know, to us as it relates to the first level of due diligence, like things like secured power or entitlement, zoning, you know, water rights. 
But then I was thinking, like, could we expand that out to do like more cool stuff like, for example, you know, put a risk factor on those items? Could it go out and actually look at and poll property value numbers down, you know, based on like the you know, tax assessments or not that will be relevant, but it certainly helps us with understanding. 
You know. Well. And moreover, like, who owns the property at the moment like things like that. And I know that there's some things that won't be able to do because, you know, for example, if you go to the, you know, Georgia revenue site or property tech site, you have to have credentials to log in and you know, get some of the data, but, you know, just trying to figure out a way to. 
Because what's happened? Dude, what's happening is I have like 40 properties. And for those 40 properties, there's at least 30 documents that are attached to them from a data room perspective. And I'm just trying to figure out a way to get this. 
So we can get spit on and I'll send you what it did, what I did already an executive summary that shows us like this is the site. These are the, you know, these boxes are checked. This is the risk that we would assign to it, you know, this is the range, you know, for that maybe we've for the range for that market to purchase, you know, blah. That makes sense. 
**Noah Rasheta | 02:41 
**Yeah. 
**Speaker 2 | 02:42 
**Because the other thing, too, is we don't have the expertise in the house to go and read these documents. 
**Noah Rasheta | 02:47 
**Uhh. 
**Speaker 2 | 02:48 
**And they're complicated. B like they're like the Essays and the Designs and the way the power is being delivered, it's complicated. Shit. 
And I don't get it, so. 
**Noah Rasheta | 02:59 
**Yeah. No, I think a trained AI agent is excellent at doing all that stuff. 
**Speaker 2 | 03:07 
**Alright, cool. Well, I'll send you what I did here in a couple of minutes and just give you an example of what I'd spit out. Then I'll just give you some highlights of what I think would be valuable. 
**Noah Rasheta | 03:18 
**Okay. 
**Speaker 2 | 03:20 
**And, like even doing research on the owner of the property. Because what I was. I was looking at one last week and or two weeks ago, and the guy and we ended up hanging up on him, but, he's been sued, like, nine times for real estate fraud. 
**Noah Rasheta | 03:39 
**Jeeve. 
**Speaker 2 | 03:41 
**So it's like, "Okay, you wouldn't... You're not somebody I'd want to do business with. But anyway, just a thought. And, yeah, if you can help, that'd be great. So I'll shoot that over to you and you could check it out. 
Yeah. And let's see what we can do because. Because honestly, we can just. And the other thing I was trying to figure out is there a way. And this is where I've really struggled. Everybody sends it in a different format, you know, like of a spreadsheet. 
But that spreadsheet has, you know, different. And this might be more complicated. It has different, we'll call it headers or title markers for the thing. So one might say power, one might say capacity, you know, and trying to build, like a just a spreadsheet that shows, you know, a snapshot of, like, the top fifteen things that we want to see. 
**Noah Rasheta | 04:24 
**Yeah. 
**Speaker 2 | 04:37 
**So I'll send you my challenge there, too, and see if we can figure it out. But yeah, if I just dump this stuff in somewhere and just have it just spit out an executive summary, that would be great. 
**Noah Rasheta | 04:47 
**That would be super easy. I actually just built one for retrieving calls for art. And it's the same issue where if a city's requesting a sculpture versus some other thing, 
they're all different formats, and I built this agent that goes and scrapes it, collects all the data, aggregates it into... It'll extract, like, "Well, they called it this, but these other guys call it that." 
It puts it into a template. So that these artists who are reviewing these... They just get the summary of all the important details, and the agent already went out and vetted everything. Who's posting it? Are they...? It gives them a score. 
If a city is requesting art versus a person, it'll research the person and decide if they're worth looking into or doing work with. It does tons of stuff like that, all for art. So this would be super fun and easy. I love building these things. 
**Speaker 2 | 05:44 
**Alright, well, let me do that. All right, I gotta take this call real quick. 
**Noah Rasheta | 05:47 
**Okay. Sounds good. 
**Speaker 2 | 05:48 
**Sorry, thanks. 

</meeting_transcript_1>

<meeting_transcript_2>

**Noah Rasheta | 00:01 
**Hey, Andrew. Good, how are you? 
**Speaker 2 | 00:06 
**Him at the airport and get ready aboard. So I have a couple of minutes so we catch up. 
**Noah Rasheta | 00:09 
**Okay, yeah, yep. 
**Speaker 2 | 00:15 
**What questions do you have for me? 
**Noah Rasheta | 00:16 
**So I was looking through the email and what I wanted to understand is you have these PDFs or documents they send you. Your goal was to extract out of that what you ended up getting in that executive summary. 
Right, okay, and then the other ones that you have pending... I will try this process with other ones. Are they all...? You said they're all a little different, right? 
**Speaker 2 | 00:34 
**Like a couple of other things that I kind of detailed in those bullets 
**Noah Rasheta | 00:51 
**They might have different info, but you're trying to extract a template, so to speak, so that you're getting the same stuff. 
**Speaker 2 | 01:01 
**Correct. 
**Noah Rasheta | 01:02 
**Okay. 
**Speaker 2 | 01:02 
**So... It's all detailed on there those things that I put on there like the summary you're looking at. So power confirming power and control of power connectivity, water and cooling, land zoning entitlements. 
Rest... Those are all the main topics and then if it... What I put in my email. There are a few other things like it'd be awesome to understand if there's a way to find out who actually owns the land or the building. 
Because a lot of times we get people bringing them to us and they're trying to flip them. So they're like... Let's say the properties are on the market for $25 million on a... For this guy, the guy that owns it. 
But then another guy comes in and he tries to sell it to me for $38 million, and then he just tries to flip it really fast. So that's what I'm trying to avoid. 
**Noah Rasheta | 01:52 
**Yeah. Okay, and most of the time on here, they will give you the address, right? 
**Speaker 2 | 02:04 
**Yeah, most of the time I get an address, yes. 
**Noah Rasheta | 02:07 
**Okay, then I think we'd be able to find all that out. 
**Speaker 2 | 02:12 
**Okay, well, I mean, that'll be awesome. 
**Noah Rasheta | 02:14 
**Yeah, let me give it a go. I just wanted to make sure I understood the process that you've been doing on this. 
**Speaker 2 | 02:26 
**I have other data rooms we can throw in there too to mess with. 
**Noah Rasheta | 02:32 
**Okay, cool. Well, I'll get started with this one, and then, yeah, you can send me another one so I can test that one too, but, yeah, I think I have what I need for now. 
**Speaker 2 | 02:49 
**Cool. All right, well, let me know, looking forward to seeing some outlets. 
**Noah Rasheta | 02:53 
**Yeah, all right. 
**Speaker 2 | 02:56 
**All right, thank you, sir. 
**Noah Rasheta | 02:57 
**Yep, thanks. 
**Speaker 2 | 02:58 
**Have a great day. Enjoy the spring, you know. 
**Noah Rasheta | 03:01 
**Yeah, you too. 
**Speaker 2 | 03:02 
**See you by... 
**Noah Rasheta | 03:02 
**See ya. 

</meeting_transcript_2>

 