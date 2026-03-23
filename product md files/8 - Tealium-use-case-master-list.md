# Tealium Use Case Master List
**Messaging Bible - Reference Source for GenAI Content Generation**

---

## How to Use This Document

This document is part of Tealium's Messaging Bible. It is a structured reference input for AI agents and GenAI systems producing marketing, sales, and campaign content. It is not end-user copy.

Each use case is tagged with its primary Answer Dimension, drawn from the four-dimension framework in the Answer document. This enables GenAI to retrieve use cases by persona group, by Answer Dimension, or by both simultaneously.

**The four Answer Dimensions:**
- **I - Real-Time Layer:** Data collection, event streaming, identity resolution, and living visitor profiles
- **II - Context Layer:** Context engineering, AI model routing, Moments API delivery, feedback loops, and AI-ready data
- **III - Orchestration Layer:** Audience management, cross-channel activation, consent governance, suppression, and measurement
- **IV - Architecture Flexibility:** Deployment modes, schema flexibility, interoperability, extensibility, and data quality infrastructure

**Current product names used throughout this document:**
- **Tealium Collect** - data collection and event streaming, web (client-side and server-side) and mobile
- **Tealium CDP** - customer profiles, identity resolution, audience management, and activation
- **Tealium Functions** - custom logic and data transformations within the pipeline
- **Predict ML** - built-in predictive modeling; scores write back to CDP profiles as first-class attributes
- **Moments API** - sub-100ms profile delivery to AI models and external systems at the moment of inference or interaction
- **Warehouse-native Audiences** - governed activation directly from cloud data warehouses without data replication
- **EventDB** - internal event logging and measurement (retained name)

---

## 1. Marketing, Growth & Paid Media Teams

### Top 3 Primary Use Cases

---

**1. Lookalike acquisition audiences for net-new customer growth**

**Answer Dimension (Primary):** III - Orchestration Layer
**Also relevant to:** I - Real-Time Layer
**Impact:** 5/5 | **Effort:** 3/5

- **Description:** Use Tealium to build high-quality seed audiences from existing high-value customers - loyalty members, repeat purchasers, or high LTV cohorts - and syndicate those into ad platforms as the basis for lookalike models. Because profiles update in real time, seed audiences stay fresh as customers buy, churn, or change behavior, which improves the underlying model and reduces waste.

  The result is more efficient prospecting: you acquire new customers who look like your best ones using first-party data, not stale lists or third-party segments. This reduces CAC, improves ROAS, and creates a scalable acquisition engine that can be tuned by product line, region, or lifecycle stage.

- **Tealium products required:**
  - Tealium Collect - web/app data collection
  - Tealium CDP - identity, profiles, audience building, activation
  - Predict ML or external ML (optional) - LTV/propensity-based seed definition
  - Ad platform connectors

- **Core KPIs:**
  - New customers acquired from lookalike campaigns
  - CAC and CPA vs broad/interest-based baselines
  - ROAS / revenue per media dollar
  - Conversion rate of lookalike campaigns vs non-Tealium baselines

---

**2. Multi-channel suppression of recent converters across all paid channels**

**Answer Dimension (Primary):** III - Orchestration Layer
**Also relevant to:** I - Real-Time Layer
**Impact:** 5/5 | **Effort:** 3/5

- **Description:** Tealium listens for conversion events (e.g., purchase, application complete, signup) from any channel and immediately updates the customer's profile. Those updates drive suppression instructions to all connected activation tools - ad platforms, email, SMS, and more - so you stop paying to advertise to people who have just converted.

  This creates a consistent, respectful experience where customers don't see "buy now" ads for things they purchased minutes ago. It also recovers wasted media spend and increases effective reach by reallocating budget away from converted users and toward net-new or still-in-funnel audiences.

- **Tealium products required:**
  - Tealium Collect - capture conversion events
  - Tealium CDP - conversion flags, suppression audiences
  - Ad, email, SMS, and personalization connectors
  - Tealium Functions (optional) - complex re-entry / post-suppression rules

- **Core KPIs:**
  - Wasted impressions avoided and equivalent saved media spend
  - ROAS / CPA improvement on affected campaigns
  - Reduction in impressions and spend to recent converters
  - Net incremental conversions from reallocated budget

---

**3. Prospect re-targeting based on high-intent behavior (e.g., product views, pricing pages)**

**Answer Dimension (Primary):** I - Real-Time Layer
**Also relevant to:** III - Orchestration Layer
**Impact:** 5/5 | **Effort:** 3/5

- **Description:** Tealium captures granular behavioral signals (product detail views, pricing page visits, configurator usage, etc.) and builds audiences that reflect different levels of purchase intent. High-intent segments can be activated immediately across channels - display, social, email, SMS - to bring prospects back to the site with tailored creative.

  Because the audiences are maintained in real time, users move in and out of segments as they progress or cool off. This allows you to structure retargeting strategies around intent thresholds (e.g., "deep product exploration but no cart") and control message frequency, offer aggressiveness, and channels based on actual engagement.

- **Tealium products required:**
  - Tealium Collect - behavioral event capture
  - Tealium CDP - intent attributes and segment logic
  - Predict ML or external models (optional) - advanced intent/propensity scoring
  - Ad, email, SMS, push, and personalization connectors

- **Core KPIs:**
  - Conversion rate of high-intent retargeting segments
  - Incremental revenue from retargeting vs no-retargeting baselines
  - CTR / engagement on retargeting campaigns
  - Cost per incremental conversion vs generic retargeting

---

### Remaining Use Cases

---

**4. Online + offline conversion tracking & CAPI integrations (Meta, Google, etc.)**

**Answer Dimension (Primary):** I - Real-Time Layer
**Also relevant to:** III - Orchestration Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Tealium unifies conversion events from web, app, call center, POS, and back-office systems, then sends normalized conversion and matching signals (emails, phone numbers, click IDs, device IDs) to platforms via Conversion APIs. This mitigates signal loss from browser restrictions and ad tracking changes by relying on server-side, first-party data.

  With more complete and timely conversion feeds, platforms can attribute more conversions correctly, improve their optimization models, and unlock features like offline conversion tracking and advanced bidding. Marketers see better ROAS, more accurate CPA/ROI reporting, and a more resilient acquisition program despite ecosystem changes.

- **Tealium products required:**
  - Tealium Collect - capture online and offline conversions (server-side)
  - Tealium CDP - identity stitching and profile enrichment
  - CAPI / ads connectors (Meta, Google, TikTok, Amazon, Snapchat, LinkedIn, etc.)
  - EventDB / Insights (optional) - internal conversion logging and QA

- **Core KPIs:**
  - Increase in attributed conversions inside ad platforms
  - ROAS and CPA improvement post-CAPI deployment
  - Reduction in observable conversion loss vs internal numbers
  - Incremental revenue from improved optimization and measurement

---

**5. Media wastage reduction via frequency capping and fatigue suppression audiences**

**Answer Dimension (Primary):** III - Orchestration Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** By centralizing impression and engagement data from multiple ad platforms, Tealium can track how often each user has been exposed to campaigns across channels. You can then build audiences for over-exposed or fatigued users and push those to platforms as suppression or "cooldown" segments, even if the platforms don't natively share that level of cross-channel insight.

  This reduces wasted impressions on users who have already seen too many ads or clearly aren't engaging. It also improves customer experience by avoiding ad fatigue, allowing you to manage frequency holistically rather than in siloed tools.

- **Tealium products required:**
  - Tealium CDP - frequency/fatigue attributes and segments
  - Tealium Collect - ingest impression and engagement data
  - Tealium Functions (optional) - custom fatigue and cooldown logic
  - Ad and messaging connectors - to apply suppression in each platform

- **Core KPIs:**
  - Reduction in impressions to over-exposed / fatigued users
  - CTR and conversion rate lift after fatigue controls are applied
  - Improvement in cost per incremental conversion
  - Declines in unsubscribe, "hide ad," or complaint rates

---

**6. Audience-based bid optimization and budget reallocation (ROAS-driven audiences)**

**Answer Dimension (Primary):** III - Orchestration Layer
**Also relevant to:** II - Context Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Many organizations miss value by treating all conversions equally in bidding strategies. Tealium can segment users by predicted or realized value (e.g., LTV bands, high-margin buyers) and feed those audiences into ad platforms with appropriate labels or lists. Media teams can then bid more aggressively on high-value segments and more conservatively on lower-value ones, regardless of platform-native support.

  This approach turns your bidding strategy from "all conversions are equal" to "invest more where value is highest," making every dollar more efficient. Over time, you can use performance feedback to refine segments and tie bidding strategies directly to business KPIs like margin or CLV, not just click-based metrics.

- **Tealium products required:**
  - Tealium CDP - value-based attributes and segmentation
  - Predict ML or external ML - CLV or profit-based scoring (strongly recommended)
  - Ad platform connectors - pass value-tier audiences or custom signals

- **Core KPIs:**
  - Profit-based ROAS (margin or CLV per media dollar)
  - Average order value and CLV of acquired cohorts
  - Media spend mix by value band (high vs low value)
  - Reduction in unprofitable spend on low-value segments

---

**7. Geo-targeted and location-aware campaigns (store proximity, region-specific offers)**

**Answer Dimension (Primary):** III - Orchestration Layer
**Also relevant to:** I - Real-Time Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** With Tealium, you can combine IP-based location, declared addresses, store visit data, and regional inventory or campaign data to create geo-aware audiences. Marketers can then run campaigns that reflect local context - promoting nearby stores, region-specific promotions, or local regulations - without hard-coding rules into each channel.

  This enables truly omnichannel geo-strategies: online messages that reflect offline store realities, localized creative by city or region, and targeted campaigns for expansion markets or underpenetrated geos. As location and behavior signals change, audiences update automatically.

- **Tealium products required:**
  - Tealium Collect - location and store interaction capture
  - Tealium CDP - geo, store-affinity, and region attributes
  - Tealium Functions (optional) - distance calculations, region mapping
  - Ad, email/SMS, and personalization connectors

- **Core KPIs:**
  - Lift in conversions or revenue in geo-targeted regions/stores
  - Engagement with localized vs generic creative (CTR, open rate)
  - Store visits / BOPIS orders where trackable
  - Reduction in impressions promoting unavailable or irrelevant offers

---

**8. Prospect prioritization using engagement / lead scoring models for MQLs**

**Answer Dimension (Primary):** II - Context Layer
**Also relevant to:** III - Orchestration Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Engagement or lead scoring models in Tealium convert many small behavioral signals - page visits, recency, content depth, channel mix - into a single score per user. Thresholds on this score drive audiences for "hot," "warm," or "cold" prospects, feeding both marketing campaigns and sales processes.

  This allows marketing to prioritize spend and messaging on prospects most likely to convert, while sales sees a clearer picture of which leads deserve outreach now. Over time, you can adjust scoring weights and thresholds based on performance data, improving both lead quality and conversion rates.

- **Tealium products required:**
  - Tealium CDP - scoring attributes, thresholds, and segments
  - Tealium Functions - custom scoring and decay logic
  - Predict ML or external ML (optional) - model-based lead scoring
  - CRM and marketing automation connectors - routing and nurture by score band

- **Core KPIs:**
  - Lead-to-opportunity and lead-to-close conversion rates
  - Average sales cycle length for "hot" vs other leads
  - MQL to SQL acceptance and conversion rates
  - Revenue per lead or per rep, segmented by score band

---

## 2. CRM, Email, and Lifecycle Marketing Teams

### Top 3 Primary Use Cases

---

**9. Cart and funnel abandonment recovery across email, SMS, paid media, and onsite**

**Answer Dimension (Primary):** III - Orchestration Layer
**Also relevant to:** I - Real-Time Layer
**Impact:** 5/5 | **Effort:** 3/5

- **Description:** Tealium identifies users who begin but don't complete key journeys - cart creation, application forms, quotes, or registration flows - by monitoring events and funnel stages. Those "abandoner" audiences trigger recovery programs across email, SMS, push, and paid media, with creatives tailored to the specific step abandoned, cart value, or product category.

  Because Tealium keeps the profile updated across channels, you can coordinate follow-up (e.g., avoid sending an abandonment email if the user already returned and converted via another channel). This improves recovered revenue, reduces duplicate or conflicting messages, and makes recovery programs more intelligent than simple one-size-fits-all reminders.

- **Tealium products required:**
  - Tealium Collect - detailed funnel and cart-stage tracking
  - Tealium CDP - abandonment attributes and segments
  - Email, SMS/push, paid media, and onsite personalization connectors
  - EventDB / Insights (optional) - funnel and performance analysis

- **Core KPIs:**
  - Recovered conversions and recovered revenue from abandonment flows
  - Conversion rate lift for contacted abandoners vs control
  - Time-to-contact after abandonment
  - Contribution of abandonment programs to overall online revenue

---

**10. Real-time web and mobile app personalization (home, category, PDP, checkout)**

**Answer Dimension (Primary):** I - Real-Time Layer
**Also relevant to:** II - Context Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Using unified profiles and real-time event streams, Tealium can pass audience and attribute flags into personalization engines or directly into data layers powering on-site logic. This supports experiences like different homepages for new vs returning visitors, product tiles ordered by affinity, or checkout flows tailored to risk profiles or loyalty status.

  By centralizing the logic in Tealium rather than every point solution, you maintain consistent segmentation and eligibility rules across all digital surfaces. That means experiments and personalization strategies can be rolled out faster and with less engineering effort, while still reflecting the latest cross-channel behavior.

- **Tealium products required:**
  - Tealium Collect - real-time event capture on web and app
  - Tealium CDP - profiles, audiences, and personalization attributes
  - Moments API - sub-100ms profile delivery to personalization engines at the moment of page load or session event
  - Connectors to personalization engines (Optimizely, Adobe Target, in-house, etc.)

- **Core KPIs:**
  - Conversion rate uplift on personalized vs non-personalized variants
  - Average order value / revenue per session for personalized experiences
  - Engagement metrics on key modules (CTR, dwell time, depth)
  - Experiment-level lift and win rate of personalization tests

---

**11. Contextual offer and promotion targeting (discount sensitivity, coupon clippers, VIPs)**

**Answer Dimension (Primary):** III - Orchestration Layer
**Also relevant to:** II - Context Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** Tealium tracks user interactions with promotions - coupon usage, sale browsing, price range, and responsiveness to discount messages - and builds audiences that reflect discount sensitivity. At the same time, it can identify VIPs or high-margin customers who don't need aggressive discounting to convert.

  Lifecycle and CRM teams can then tailor their promotional strategy: offer deeper discounts to price-sensitive segments, limit or withhold discounts for full-price buyers, and construct offers that protect margin. Over time, these patterns inform promotion calendars and reduce blanket discounting that erodes profitability.

- **Tealium products required:**
  - Tealium Collect - promo, coupon, and price-band behavior
  - Tealium CDP - discount-sensitivity, VIP, and value attributes
  - Email, SMS/push, ads, and personalization connectors

- **Core KPIs:**
  - Margin per order and overall promotion-driven margin
  - Offer redemption rate by segment (price-sensitive vs full-price segments)
  - Revenue lift from targeted promotions vs blanket discounts
  - Reduction in total discount spend with stable or growing revenue

---

### Remaining Use Cases

---

**12. Personalized product recommendations and next-best product experiences**

**Answer Dimension (Primary):** II - Context Layer
**Also relevant to:** III - Orchestration Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** By aggregating purchase history, browsing behavior, product affinities, and potentially AI-based recommendation scores, Tealium enables activation of "next best product" across email, push, on-site modules, and ads. The same recommendation logic can power multiple channels because Tealium coordinates both inputs (signals) and outputs (audiences and attributes).

  This unifies what customers see - so the product recommended in their follow-up email aligns with what's promoted in retargeting ads or on the homepage. It increases cross-sell and upsell rates, raises average order value, and creates a more coherent brand experience.

- **Tealium products required:**
  - Tealium Collect - product, category, and purchase events
  - Tealium CDP - affinity and recency/frequency attributes
  - Predict ML or external recommendation engine - recommendation logic
  - Email, push, onsite/app, and paid media connectors

- **Core KPIs:**
  - Cross-sell/upsell conversion rate on recommended items
  - Average order value uplift when recommendations are shown
  - Incremental revenue attributed to recommendation placements
  - CTR and add-to-cart from recommendation modules

---

**13. Landing-page personalization for paid media (campaign-, audience-, or keyword-based)**

**Answer Dimension (Primary):** I - Real-Time Layer
**Also relevant to:** II - Context Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** Tealium captures campaign metadata (UTM parameters, click IDs, referrers) and associates it with visitor profiles. This data, combined with audience membership and behavior, can be used to personalize landing pages: show different messaging, offers, or content modules depending on which campaign or keyword brought the user in.

  Because personalization is based on Tealium's unified view rather than just URL parameters, you can handle complex scenarios like returning visitors from multiple campaigns, dynamic remarketing journeys, or cross-channel re-engagement, all while ensuring the experience matches the user's full history.

- **Tealium products required:**
  - Tealium Collect - UTM, click ID, and campaign data capture
  - Tealium CDP - campaign attributes and segments
  - Tealium Functions (optional) - campaign-to-experience mapping logic
  - Data layer outputs / personalization connectors for landing pages

- **Core KPIs:**
  - Landing-page conversion rate by campaign/keyword with personalization
  - Bounce rate and time-on-page improvements vs generic landers
  - Down-funnel metrics: qualified leads, revenue per click
  - Incremental revenue lift of personalized vs non-personalized landing pages

---

**14. Multi-step form and application drop-off recovery (e.g., insurance, finance, telco)**

**Answer Dimension (Primary):** III - Orchestration Layer
**Also relevant to:** I - Real-Time Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** For complex, multi-step flows such as credit applications, policy quotes, or service sign-ups, Tealium tracks exactly where and when users drop off. It builds audiences that reflect specific abandonment points and reasons (e.g., missing documentation, pricing shock, eligibility issues) and can trigger targeted outreach or alternate paths.

  Lifecycle teams can then design journeys that address the source of friction: additional education content, personalized assistance, alternate products, or reminders to complete the process. This is especially powerful in industries where a single conversion represents high value and follow-up timing is critical.

- **Tealium products required:**
  - Tealium Collect - step-level and abandon event tracking
  - Tealium CDP - stage-specific abandonment attributes and segments
  - Connectors - email/SMS, call center, paid media, web/app messaging
  - EventDB / Insights (optional) - funnel diagnostics, step-performance analysis

- **Core KPIs:**
  - Completion rate for multi-step forms/applications
  - Number and value of applications recovered via follow-up
  - Time to follow-up after drop-off and its impact on completion
  - Incremental revenue or policy/contract volume from recovery flows

---

**15. A/B and multivariate testing audiences (consistent test/control across channels)**

**Answer Dimension (Primary):** III - Orchestration Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** Tealium can assign visitors to test and control groups using deterministic rules or randomization and then maintain those assignments as audiences across every activation tool. This ensures a user in "Test A" sees the corresponding experiences in email, web, ads, and push, not just in one channel.

  This centralization of experiment cohorts simplifies experimentation at scale and improves the validity of results. Teams can run more sophisticated multi-channel tests (e.g., different full-funnel treatments) while keeping measurement clean and consistent.

- **Tealium products required:**
  - Tealium CDP - experiment cohort attributes and audiences
  - Tealium Functions (optional) - randomization and cohort logic
  - Connectors - ensure cohorts are respected in ESP, ad, and personalization tools
  - EventDB / warehouse feed - experiment data for analysis

- **Core KPIs:**
  - Lift (conversion, revenue, engagement) by variant vs control
  - Cohort integrity (low cross-over / contamination between test and control)
  - Number and complexity of cross-channel experiments run per period
  - Time to design, run, and analyze experiments end-to-end

---

**16. Upsell and cross-sell campaigns based on purchase history and browsing behavior**

**Answer Dimension (Primary):** III - Orchestration Layer
**Also relevant to:** II - Context Layer
**Impact:** 5/5 | **Effort:** 3/5

- **Description:** By unifying transactional and behavioral data, Tealium identifies customers who bought product A but not the natural complement, or a base plan but not premium, or who own a given product and are now researching adjacent ones. These audiences fuel upsell and cross-sell campaigns across all channels, with messaging tailored to the specific product relationships.

  Because the underlying logic is in Tealium, it's easy to adapt by vertical (add-on coverages in insurance, bundles in retail, add-on services in telco) and to tie campaigns to margin or strategic focus areas. This drives more revenue from existing customers while improving relevance.

- **Tealium products required:**
  - Tealium Collect - product, category, and purchase events
  - Tealium CDP - purchase history, browsing affinity, and product-gap attributes
  - Predict ML or external recommendation engine (optional)
  - Email, push, onsite/app, and paid media connectors

- **Core KPIs:**
  - Cross-sell/upsell conversion rate from targeted campaigns
  - Average order value and revenue per customer in targeted segments
  - Incremental revenue from expansion vs baseline
  - Margin contribution from upsell products

---

**17. Churn prediction and churn-prevention / win-back programs**

**Answer Dimension (Primary):** II - Context Layer
**Also relevant to:** III - Orchestration Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Tealium ingests behavioral signals like declining engagement, negative feedback, support tickets, and billing events, and can either host or import churn propensity scores. Customers at risk of leaving are placed into retention audiences that drive proactive outreach, targeted offers, or experience improvements before cancellation occurs.

  For those who have already churned, Tealium can segment by reason, value, or history to power win-back campaigns with tailored positioning. This coordinated approach helps reduce churn, protect revenue, and focus limited retention budgets on the customers who matter most.

- **Tealium products required:**
  - Tealium Collect - behavioral and account-event signals
  - Tealium CDP - churn risk attributes and at-risk audience segments
  - Predict ML or external ML - churn propensity scoring
  - Email, SMS/push, call center, and paid media connectors

- **Core KPIs:**
  - Churn rate reduction for at-risk segments with proactive outreach
  - Revenue retained from successful churn-prevention programs
  - Win-back rate for churned customers
  - ROI of retention and win-back campaigns vs new acquisition cost

---

**18. Lapsed-customer win-back (time-since-last-purchase or last-engagement driven)**

**Answer Dimension (Primary):** III - Orchestration Layer
**Impact:** 4/5 | **Effort:** 2/5

- **Description:** Time-based metrics like "days since last purchase" or "days since last engagement" are calculated in Tealium and used to define lapsed segments (e.g., 30, 60, 90 days). Lifecycle marketers then design win-back sequences with escalating tactics: soft reminders, new content, offers, or cross-channel outreach for dormant but high-value customers.

  Because these attributes and audiences are dynamic, customers move into and out of lapsed segments automatically. This ensures win-back efforts target the right people at the right time and don't conflict with other campaigns.

- **Tealium products required:**
  - Tealium CDP - time-based lapse attributes and segment logic
  - Tealium Collect - engagement events that reset lapse timers
  - Email, SMS/push, and paid media connectors
  - Predict ML (optional) - value-weighted prioritization of win-back candidates

- **Core KPIs:**
  - Win-back rate by lapsed cohort (30/60/90-day segments)
  - Revenue recovered from reactivated lapsed customers
  - CAC comparison: win-back vs new customer acquisition
  - Reduction in average days-lapsed at reactivation over time

---

**19. Onboarding and nurture journeys (from first touch to first value)**

**Answer Dimension (Primary):** III - Orchestration Layer
**Also relevant to:** I - Real-Time Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Tealium connects early-stage signals - first website visit, resource downloads, initial product usage - with downstream events like sign-ups, purchases, or feature adoption. These signals feed onboarding and nurture journeys that adapt based on actions taken (or not taken) across channels.

  For example, a new customer who has not completed profile setup or used a key feature can receive targeted education emails, in-app prompts, and retargeting. Once they reach "activation" or "first value," Tealium moves them into different lifecycle streams. This dynamic orchestration strengthens early retention and accelerates time to value.

- **Tealium products required:**
  - Tealium Collect - first-touch and early-stage event capture
  - Tealium CDP - onboarding stage attributes and progression logic
  - Email, SMS/push, in-app, and paid media connectors
  - Predict ML (optional) - activation propensity scoring

- **Core KPIs:**
  - Time to first value / activation event
  - Onboarding completion rate
  - Feature adoption rate for new customers
  - Early-stage churn rate with vs without structured onboarding journeys

---

**20. Loyalty program activation and tier-based experiences (earn, burn, status, perks)**

**Answer Dimension (Primary):** III - Orchestration Layer
**Also relevant to:** I - Real-Time Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** Loyalty data (points, tiers, status, available rewards) can be ingested into Tealium and surfaced as attributes in customer profiles. Using those, marketers create audiences for high tiers, near-tier upgrades, point expiry risk, or specific reward eligibilities and activate differentiated treatments across channels.

  This lets you build consistent loyalty experiences: emails that promote specific rewards, on-site banners tailored to status, VIP early access segments in paid media, and more. It also helps you drive desired behaviors such as earning, redeeming, or moving up tiers.

- **Tealium products required:**
  - Tealium Collect - loyalty event and transaction capture
  - Tealium CDP - loyalty tier, points balance, and status attributes
  - Loyalty platform connectors (ingest and activation)
  - Email, SMS/push, onsite/app, and paid media connectors

- **Core KPIs:**
  - Loyalty member engagement rate (earn, redeem, status activity)
  - Tier upgrade rate among targeted segments
  - Redemption-driven revenue
  - CLTV differential between active loyalty members and non-members

---

**21. VIP / high-LTV programs and white-glove treatment segments**

**Answer Dimension (Primary):** III - Orchestration Layer
**Also relevant to:** II - Context Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** Tealium calculates or imports customer lifetime value (CLV), total purchase count, and other value indicators, then uses them to define VIP cohorts. These segments can receive heightened service levels, exclusive offers, dedicated support routes, or premium experiences in all channels.

  Because profiles are updated as customers spend more or less, VIP status can be dynamic or multi-tiered. This helps allocate resources and benefits to customers who drive disproportionate value, while also supporting "emerging VIP" programs for promising segments.

- **Tealium products required:**
  - Tealium CDP - CLV, purchase frequency, and value attributes
  - Predict ML or external ML - CLV scoring and tier assignment
  - All channel connectors (VIP treatment spans every touchpoint)

- **Core KPIs:**
  - Revenue share from top-tier VIP segments
  - Retention rate of VIP vs non-VIP customers
  - Engagement uplift from VIP-specific treatments
  - CLTV growth rate for emerging-VIP cohorts

---

**22. Occasion-based, birthday, or lifecycle milestone campaigns**

**Answer Dimension (Primary):** III - Orchestration Layer
**Impact:** 3/5 | **Effort:** 2/5

- **Description:** Date-based attributes such as birthdays, anniversaries, signup dates, or lifecycle milestones are captured and transformed into trigger conditions in Tealium. Marketers can then build automations around these occasions, delivering timely, relevant messages that feel personal rather than generic.

  These campaigns often drive high engagement and can be layered with other segments (e.g., high-value birthday offers, milestone celebrations for long-tenured customers). Tealium's role is to maintain the underlying date logic and orchestrate it across tools.

- **Tealium products required:**
  - Tealium CDP - date-based attributes and trigger logic
  - Tealium Functions - date calculations and milestone logic
  - Tealium Collect - declared date inputs (birthday capture, signup events)
  - Email, SMS/push, and paid media connectors

- **Core KPIs:**
  - Occasion campaign open and conversion rates vs standard campaigns
  - Revenue lift from occasion-triggered sends
  - Engagement rate for milestone messages
  - Reduction in campaign fatigue from better-timed, relevant sends

---

**23. Subscription renewal, upgrade, and save-the-cancel journeys**

**Answer Dimension (Primary):** III - Orchestration Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** For subscription or contract businesses, Tealium tracks renewal dates, plan types, payment events, and cancellation signals (e.g., downgrade, negative feedback). This forms audiences for upcoming renewals, renewal at risk, save-the-cancel, and upgrade opportunities.

  Lifecycle teams leverage these to run systematic outreach before and after key moments - pre-renewal education and offers, targeted upsell before contract end, and tailored save-the-cancel flows that depend on why a customer is leaving. This helps stabilize recurring revenue and create predictable interventions.

- **Tealium products required:**
  - Tealium Collect - cancellation signals, billing, and account events
  - Tealium CDP - renewal date attributes, plan-type segments, and save-the-cancel flags
  - Predict ML or external ML (optional) - renewal risk scoring
  - Email, SMS/push, and call center connectors

- **Core KPIs:**
  - Renewal rate with vs without proactive journey
  - Revenue saved from successful save-the-cancel flows
  - Upgrade rate from pre-renewal outreach
  - Average contract value change from upgrade campaigns

---

## 3. Digital Product, Web & eCommerce Teams

### Top 3 Primary Use Cases

---

**24. Unified identity and profile stitching across devices and channels**

**Answer Dimension (Primary):** I - Real-Time Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Tealium collects identifiers from web, app, email, CRM, call center, and offline systems, then stitches them into a single, persistent profile when linkage events (logins, form fills, purchases) occur. This allows the same person to be recognized across devices and sessions, even as cookies expire or browsers change.

  Product and eCommerce teams can then rely on a unified view of behavior and history when designing experiences, experiments, or recommendations. It also boosts analytics quality and makes cross-device attribution more accurate.

- **Tealium products required:**
  - Tealium Collect - capture IDs and events across web, app, and server-side
  - Tealium CDP - identity resolution, stitching rules, persistent profiles
  - Connectors to CRM / call center / POS (optional but common)

- **Core KPIs:**
  - % of traffic / customers successfully identity-resolved across channels
  - Reduction in duplicate profiles across systems
  - Improvement in cross-device attribution accuracy
  - Uplift in performance of profile-dependent use cases (personalization, retargeting)

---

**25. Data-layer standardization across sites and apps (clean, consistent behavioral data)**

**Answer Dimension (Primary):** IV - Architecture Flexibility
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Tealium helps define a canonical data layer - standard event names, attributes, and structures - across websites and applications. Tags, SDKs, and server-side collection then map raw signals into this normalized schema, ensuring consistency regardless of source.

  This reduces the burden on product and engineering teams when adding new tools or features: once data is in the standardized layer, it can be reused everywhere. It also reduces data quality issues and makes downstream analytics and activation more reliable.

- **Tealium products required:**
  - Tealium Collect - client-side data layer definition and enforcement, app-side event and attribute mapping
  - Tealium Functions (optional) - advanced normalization / mapping logic

- **Core KPIs:**
  - Data quality metrics (missing/invalid fields, schema violations)
  - Time to onboard new tools / tags using standardized data layer
  - Reduction in one-off tracking patches or custom code in apps/sites
  - Analyst satisfaction / reduced time spent cleaning/joining data

---

**26. Guided selling, quizzes, and zero-party data capture feeding into profiles and audiences**

**Answer Dimension (Primary):** I - Real-Time Layer
**Also relevant to:** II - Context Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** Interactive experiences like product finders, quizzes, and preference centers capture zero-party data (explicit user input about needs, preferences, or intent). Tealium ingests and stores these as profile attributes, allowing segmentation and personalization based on what customers say they want, not just what they do.

  Digital teams can then tailor site experiences, content, and product recommendations using this data, while marketers leverage it for campaigns. Because the data is structured and consent-aware, it's especially valuable as passive tracking signals degrade.

- **Tealium products required:**
  - Tealium Collect - capture quiz/form/preference submissions
  - Tealium CDP - store declared preferences as profile attributes and segments
  - Connectors - email/SMS, personalization, and ad platforms using these attributes

- **Core KPIs:**
  - Participation and completion rate of guided selling / quiz flows
  - Volume and richness of zero-party attributes per profile
  - Conversion and engagement uplift for users with declared preferences vs without
  - Impact on recommendation relevance and promotion performance

---

### Remaining Use Cases

---

**27. Inventory- and availability-aware messaging (low stock, back-in-stock, alternative products)**

**Answer Dimension (Primary):** III - Orchestration Layer
**Also relevant to:** I - Real-Time Layer
**Impact:** 4/5 | **Effort:** 4/5

- **Description:** Tealium can integrate with inventory systems or data warehouses to bring inventory status into the experience layer. That enables use cases like low-stock urgency messaging, back-in-stock alerts, or automatic promotion of alternative products when a selected item is unavailable.

  By tying inventory data to customer profiles and behavioral events, you can ensure that high-intent sessions don't dead-end on out-of-stock items. Instead, you dynamically route users to viable alternatives or capture their intent for later follow-up.

- **Tealium products required:**
  - Tealium Collect - product views, cart actions, back-in-stock triggers
  - Tealium CDP - "interest in product X" and inventory-aware flags
  - Tealium Functions - connect to inventory/warehouse APIs mid-stream
  - Email, SMS/push, and personalization connectors

- **Core KPIs:**
  - Back-in-stock notification opt-ins and conversion rate
  - Reduction in exits from out-of-stock pages/flows
  - Revenue recovered by alternative product suggestions
  - Sell-through of inventory using urgency and availability messaging

---

**28. Store-finder and "buy online, pick up in store" (BOPIS) journey optimization**

**Answer Dimension (Primary):** III - Orchestration Layer
**Also relevant to:** I - Real-Time Layer
**Impact:** 4/5 | **Effort:** 4/5

- **Description:** Location data, store information, and customer behavior are combined in Tealium to power experiences such as store pickers, BOPIS journeys, or local store promotions. For example, users who choose a preferred store or use store-finder tools can be profiled and later targeted with store-specific offers or reminders.

  This creates a bridge between digital and physical retail experiences. eCommerce and product teams can track full journeys that blend online research, store visits, and pickup events, and then optimize friction points based on that insight.

- **Tealium products required:**
  - Tealium Collect - store finder use, store selection, and BOPIS events (web/app and server-side)
  - Tealium CDP - preferred store attributes, BOPIS usage segments
  - Connectors - email/SMS, push, ads, and onsite/app personalization

- **Core KPIs:**
  - BOPIS orders and completion rate
  - Store visits / pick-up rates tied to digital interactions
  - Conversion rate for users who interact with store-finder or set preferred store
  - Average order value or repeat purchase behavior for BOPIS users vs non-BOPIS

---

**29. Omnichannel experience continuity (online to store, store to online, call center to web)**

**Answer Dimension (Primary):** III - Orchestration Layer
**Also relevant to:** I - Real-Time Layer
**Impact:** 5/5 | **Effort:** 5/5

- **Description:** Tealium centralizes events and profile updates from all touchpoints - including POS, kiosks, call centers, and web/apps - so downstream experiences can reflect what just happened elsewhere. A support call can influence on-site messaging, an in-store purchase can inform online recommendations, and an online configuration can be pulled up in a store or call center.

  This continuity means customers don't have to re-explain themselves, and experiences can pick up where they left off regardless of channel. It also gives digital teams a richer picture for experimentation and product improvement.

- **Tealium products required:**
  - Tealium Collect - digital interactions and server-side ingest of offline/POS/call center events
  - Tealium CDP - unified cross-channel profiles and signals
  - Connectors - to store systems, call center, personalization, and marketing tools

- **Core KPIs:**
  - % of interactions orchestrated across two or more channels
  - Drop-off rate between channel transitions (e.g., web to store, call to web)
  - Customer satisfaction / NPS for omnichannel journeys
  - Revenue or retention lift for customers experiencing seamless continuity

---

**30. Dynamic content and layout personalization (hero banners, navigation, recommendations)**

**Answer Dimension (Primary):** II - Context Layer
**Also relevant to:** I - Real-Time Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** Using profile attributes and audience membership, Tealium can feed personalization platforms or front-end logic with signals that decide which hero banners, navigation items, promos, or modules to show. For instance, new users might see educational content, while returning buyers see promotions or recommendations.

  Because the segmentation logic is centralized, product teams can test and iterate on rules without rewriting application code for every variation. This speeds up experimentation and supports more nuanced content strategies.

- **Tealium products required:**
  - Tealium Collect - data layer hooks for personalization
  - Tealium CDP - segments and attributes driving content decisions
  - Moments API - delivers current-state profile to CMS/personalization systems at page load
  - Connectors to CMS/personalization systems

- **Core KPIs:**
  - Conversion rate and engagement uplift for personalized content slots
  - Click-through and interaction with personalized navigation/elements
  - Experiment win rate (personalized variants vs control)
  - Revenue per session for users exposed to dynamic content

---

**31. Experimentation support: segment-based personalization and test/control management**

**Answer Dimension (Primary):** III - Orchestration Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** Tealium can create and manage experimental cohorts as audiences and ensure that all tools respect those boundaries. For example, an A/B test on site can be mirrored by different email or ad treatments for the same users, enabling full-funnel experiments.

  This simplifies coordination between product, marketing, and analytics teams. It also ensures that analysis can be done against consistent cohorts, improving confidence in the results and enabling more ambitious experiment designs.

- **Tealium products required:**
  - Tealium CDP - experiment cohort flags and audience management
  - Tealium Functions (optional) - randomization / deterministic assignment logic
  - Connectors - enforce cohorts in ESP, ad platforms, and personalization tools
  - EventDB / warehouse feed - experiment-level data for analysis

- **Core KPIs:**
  - Number and complexity of cross-channel experiments run
  - Statistical power and validity of experiments (low contamination)
  - Average time from experiment design to result and rollout
  - Total incremental revenue or KPI lift generated by winning variants

---

## 4. Customer Experience, Call Center & Service Teams

### Top 3 Primary Use Cases

---

**32. 360-degree customer view in the contact center (recent behavior, products, tickets, sentiment)**

**Answer Dimension (Primary):** II - Context Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** By pulling together digital behavior, purchase history, support tickets, and AI signals into a single profile, Tealium can expose a summarized customer view to call center agents in real time. When a call comes in, the agent sees who the customer is, what they've done recently, and any outstanding issues or opportunities.

  This context helps agents resolve issues faster, avoid asking customers to repeat information, and seize upsell or cross-sell moments that are actually relevant. It also supports more personalized and empathetic interactions.

- **Tealium products required:**
  - Tealium Collect - capture recent digital behavior and ingest offline events (orders, tickets, account actions)
  - Tealium CDP - unified profiles and summarized attributes
  - Moments API - sub-100ms delivery of the full profile to the agent desktop at the moment the call connects
  - Predict ML / external ML (optional) - sentiment, churn, LTV scores
  - Connectors to call center / agent desktop (e.g., Amazon Connect, Talkdesk, custom UI)

- **Core KPIs:**
  - Average handle time (AHT) and first-contact resolution (FCR)
  - CSAT / NPS after service interactions
  - Upsell / cross-sell conversion rate from service calls
  - Agent productivity and adherence to CX playbooks

---

**33. Real-time call routing based on profile, value, propensity, or sentiment signals**

**Answer Dimension (Primary):** II - Context Layer
**Also relevant to:** III - Orchestration Layer
**Impact:** 5/5 | **Effort:** 5/5

- **Description:** Tealium can send enriched profile data and predictive scores (e.g., VIP status, churn risk, sentiment) to call routing systems, influencing which queue or agent a call goes to. High-value or at-risk customers might be routed to experienced agents, while simple inquiries go to self-service or general queues.

  By aligning routing with customer value and intent, CX teams improve both efficiency and outcomes: high-impact calls are handled by the right people, and overall wait times and transfer rates are reduced.

- **Tealium products required:**
  - Tealium Collect - ingest and emit call events and routing triggers
  - Tealium CDP - value, risk, and segment attributes on profiles
  - Predict ML / external ML - churn, LTV, sentiment, next-best-action scoring
  - Connectors to call center platforms (e.g., Amazon Connect, Talkdesk, custom IVR)

- **Core KPIs:**
  - Service level metrics (speed of answer, queue times) by segment
  - FCR and escalation rates for high-value / at-risk segments
  - Churn and retention for customers routed to high-touch experiences
  - Revenue influenced by routed service/sales calls

---

**34. Agent assist and next-best-action recommendations (service or sales)**

**Answer Dimension (Primary):** II - Context Layer
**Impact:** 5/5 | **Effort:** 5/5

- **Description:** When call center systems receive Tealium's profile and propensity data, they can power agent assist tools that recommend next-best actions: troubleshooting steps, relevant offers, or retention tactics. These can be rule-based (if X then Y) or driven by AI models that use Tealium's data as input.

  Agents get real-time guidance tailored to each customer, rather than relying solely on scripts or intuition. This improves consistency, conversion on offers, and overall customer satisfaction.

- **Tealium products required:**
  - Tealium CDP - unified profile context and segment membership
  - Moments API - delivers fully assembled customer context to agent assist tools and decisioning engines at the moment of call
  - Predict ML / external ML - next-best-action, propensity, or recommendation models
  - Tealium Collect - real-time event feed to and from agent-assist / decisioning tools
  - Connectors to call center desktop and decisioning/orchestration engines

- **Core KPIs:**
  - Offer acceptance / upsell conversion rate during calls
  - CSAT / NPS impact when next-best-action is used vs not used
  - Average handle time and resolution consistency
  - Churn reduction among at-risk customers receiving NBA-led interventions

---

### Remaining Use Cases

---

**35. Triggering post-call outreach journeys (surveys, apologies, offers, follow-ups)**

**Answer Dimension (Primary):** III - Orchestration Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** After each call, Tealium can ingest call disposition, satisfaction scores, or sentiment outputs and translate them into audiences for post-call journeys. Positive experiences might trigger review or referral requests; negative ones may prompt apology offers, manager callbacks, or targeted retention outreach.

  This closes the loop between service and marketing, ensuring that significant service interactions are reflected in downstream communication strategies. It also supports continuous improvement by tying CX programs to measurable outcomes.

- **Tealium products required:**
  - Tealium Collect - ingest call completion events, dispositions, survey results
  - Tealium CDP - post-call attributes (e.g., "recent detractor," "promoter") and segments
  - Email/SMS/push connectors - survey, apology, and retention journeys
  - Predict ML / external ML (optional) - sentiment or topic models on transcripts

- **Core KPIs:**
  - Survey response rate and NPS/CSAT score trends
  - Follow-up outreach response and conversion (e.g., save-the-cancel, win-back)
  - Reduction in repeat contacts for unresolved issues
  - Churn and retention outcomes for negative-experience segments

---

**36. Proactive outreach to at-risk or high-value customers identified via churn or LTV models**

**Answer Dimension (Primary):** II - Context Layer
**Also relevant to:** III - Orchestration Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Tealium's integration with AI and data platforms allows churn and LTV scores to be attached to customer profiles. Those scores can drive outreach priorities in both marketing and service - e.g., a list of at-risk high-value customers for proactive check-ins or value-add calls.

  This "proactive service" strategy transforms CX from purely reactive to anticipatory. It can significantly reduce churn among key segments and create a differentiated experience where customers feel looked after before problems escalate.

- **Tealium products required:**
  - Tealium CDP - churn, LTV, and risk attributes on profiles
  - Predict ML / external ML - generate churn and LTV scores
  - Tealium Collect - sync to outreach tools and call-center work queues
  - Connectors - email/SMS/push, call center, and CRM for proactive tasks

- **Core KPIs:**
  - Churn rate among at-risk segments with vs without proactive outreach
  - Retention and expansion revenue from high-value proactive contacts
  - Response rates to proactive service or check-in campaigns
  - NPS / CSAT changes in high-value segments over time

---

**37. Integration of call-center data back into Tealium for cross-channel orchestration**

**Answer Dimension (Primary):** III - Orchestration Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** Call center platforms can send detailed call events, dispositions, and outcomes into Tealium, enriching profiles with service history. Those attributes - like recent complaints, upsell declines, or support topics - can then shape marketing and product experiences.

  For example, a customer who recently had a negative service experience might be suppressed from aggressive upsell campaigns or receive more helpful content instead. This integration prevents channel silos from working at cross-purposes and improves overall customer sentiment.

- **Tealium products required:**
  - Tealium Collect - ingest call events, disposition, and post-call data
  - Tealium CDP - service-history attributes and derived segments
  - Connectors - marketing, personalization, and product analytics tools
  - Predict ML / external ML (optional) - use service data in churn or LTV models

- **Core KPIs:**
  - Reduction in tone-deaf campaigns after negative service experiences
  - CSAT / NPS trend post-integration across journeys
  - Conversion and engagement for customers with positive vs negative recent service history
  - Decrease in repeat issues or complaints after service-informed orchestration

---

## 5. Data, Analytics & Customer Insights Teams

### Top 3 Primary Use Cases

---

**38. Unified customer profile and identity resolution across all sources**

**Answer Dimension (Primary):** I - Real-Time Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Tealium acts as the identity and profile layer that unifies disparate identifiers (cookies, device IDs, emails, customer IDs, phone numbers) across all systems. It maintains persistent profiles with stitched histories, so analytics and insights teams can work from a single, authoritative view of each customer.

  This simplifies analyses such as journey mapping, cohort behavior, or CLV modeling. It also reduces the time analysts spend cleaning and joining data, freeing them to focus on insight generation and decision support.

- **Tealium products required:**
  - Tealium Collect - device and session identifiers, and ingest IDs and events from backend, CRM, POS, etc.
  - Tealium CDP - identity resolution, stitching rules, persistent profiles
  - Connectors to CDW/BI for unified analytical datasets

- **Core KPIs:**
  - % of records with unified, multi-source profiles
  - Reduction in analyst time spent on identity stitching and data wrangling
  - Accuracy of customer counts across systems (fewer duplicates)
  - Improved reliability of downstream models (CLV, propensity, churn)

---

**39. Journey analytics and funnel diagnostics using complete real-time event streams**

**Answer Dimension (Primary):** I - Real-Time Layer
**Impact:** 5/5 | **Effort:** 3/5

- **Description:** Because Tealium sits in the data collection path for digital and offline touchpoints, it has a comprehensive view of events across the journey. Analysts can use Tealium-fed data in downstream tools (CDW, BI, specialized journey analytics) to understand drop-off points, channel interactions, and key drivers of conversion or churn.

  Real-time streams also support more agile analysis: teams can see how changes impact behavior quickly, enabling faster iterations and more responsive optimization.

- **Tealium products required:**
  - Tealium Collect - digital event collection and server-side streaming into CDW/BI tools
  - Tealium CDP (optional) - journey-related attributes (e.g., funnel stage)
  - Connectors to warehouses (Snowflake, Databricks, BigQuery) and BI

- **Core KPIs:**
  - Coverage and latency of event data across key touchpoints
  - Time to diagnose funnel issues (from question to answer)
  - Conversion and drop-off rates across funnel stages and channels
  - Number of journey insights that result in implemented optimizations

---

**40. Audience discovery and segmentation (VIPs, window shoppers, bargain hunters, loyalists)**

**Answer Dimension (Primary):** III - Orchestration Layer
**Also relevant to:** II - Context Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** With standardized behavioral and transactional data, analytics teams can explore and define meaningful segments based on engagement intensity, category interests, discount behavior, loyalty, or value metrics. These definitions are implemented in Tealium as audiences that can be activated directly.

  This closes the gap between insight and action: once analysts find a valuable pattern (e.g., "high-intent window shoppers"), marketers can immediately use that segment in campaigns without rebuilding logic in each tool.

- **Tealium products required:**
  - Tealium Collect - foundational clickstream data
  - Tealium CDP - implement and store discovered segment definitions
  - Connectors to activation tools (ESP, ads, personalization, etc.)

- **Core KPIs:**
  - Number of meaningful segments discovered and implemented
  - Performance of new segments vs legacy broad segments (conversion, revenue)
  - Time from analytical discovery to activation of a new segment
  - Revenue / engagement uplift from campaigns using analytics-derived audiences

---

### Remaining Use Cases

---

**41. Predictive insights: propensity, churn, LTV, and next-best-action signals**

**Answer Dimension (Primary):** II - Context Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Predictive models built in external platforms or Tealium's own ML capabilities can ingest Tealium's clean behavioral data and return scores back into profiles. These include purchase propensity, churn risk, CLV, or recommended actions/content.

  Analytics teams oversee the models and monitor performance, while Tealium ensures these signals are consistently available for activation and measurement. This creates a virtuous cycle where model outputs are applied in-market and performance data feeds back into model improvement.

- **Tealium products required:**
  - Tealium Collect - send standardized data to ML/modeling environments
  - Tealium CDP - store and expose scores on profiles
  - Predict ML or external ML infrastructure - training and scoring
  - Connectors to activation tools to use the scores (email, ads, CX, etc.)

- **Core KPIs:**
  - Model performance metrics (AUC, accuracy, lift) for propensity/churn/LTV
  - Business impact from using scores (incremental conversions, reduced churn)
  - Adoption of predictive signals across channels and teams
  - Time to refresh or retrain models with new data

---

**42. Marketing attribution and media ROI analysis using online + offline conversions**

**Answer Dimension (Primary):** III - Orchestration Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** By centralizing conversion events from multiple systems and tying them to identity-resolved profiles, Tealium improves the completeness and accuracy of attribution data. This can feed multi-touch attribution models, incrementality tests, or simple last-touch analyses in downstream analytics environments.

  Insights teams can then quantify performance across channels and campaigns with higher confidence. They can also run pro forma value analyses for key use cases, linking Tealium-powered initiatives directly to revenue and savings.

- **Tealium products required:**
  - Tealium Collect - capture conversions and marketing touches (server-side and client-side)
  - Tealium CDP - identity stitching to link touches and conversions
  - Connectors to CDW - event streams for attribution modeling
  - EventDB / Insights (optional) - quick attribution and KPI views

- **Core KPIs:**
  - Accuracy and stability of attribution results vs internal benchmarks
  - ROAS and incremental lift metrics per channel and campaign
  - Time to run attribution or incrementality analyses
  - Frequency with which attribution insights drive budget shifts

---

**43. Operationalizing mobile data across the full lifecycle (analytics + activation)**

**Answer Dimension (Primary):** I - Real-Time Layer
**Also relevant to:** III - Orchestration Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** Tealium's mobile SDK and server-side collection send app usage events into the same pipeline as web and offline data. This allows analysts to see how app behavior fits into the broader journey and to derive insights such as app-specific retention drivers or conversion paths.

  Because the same data powers activation, insights (e.g., "power users of feature X") can quickly translate into targeted campaigns or in-app personalization. This makes mobile a first-class citizen in both analytics and activation strategies.

- **Tealium products required:**
  - Tealium Collect (mobile SDK) - in-app behavioral event capture
  - Tealium Collect - streaming app data to CDW/analytics and back
  - Tealium CDP - mobile-related attributes and audiences
  - Connectors - in-app messaging, push, email/SMS, and ads

- **Core KPIs:**
  - App engagement and retention metrics by segment (DAU/MAU, stickiness)
  - Conversion and monetization metrics tied to app feature usage
  - Speed from mobile insight (e.g., feature adoption pattern) to activation
  - Incremental revenue or retention lift from mobile-informed campaigns

---

**44. Test/control governance and experiment measurement frameworks**

**Answer Dimension (Primary):** III - Orchestration Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** Tealium-managed test and control audiences provide a reliable backbone for measuring incremental impact of campaigns, features, and experiences. Analytics teams can trust that membership in these cohorts is stable and consistent across tools, simplifying data extraction and analysis.

  This supports more rigorous experimentation practices, including cross-channel tests and long-running holdouts. Ultimately, it elevates the organization's ability to connect activity to causally sound results.

- **Tealium products required:**
  - Tealium CDP - manage and persist test/control flags
  - Tealium Functions (optional) - randomization / cohort selection
  - Tealium Collect - experiment event data streamed to CDW
  - Connectors - enforce cohorts across channels and tools

- **Core KPIs:**
  - Number and quality of controlled experiments run (by team/time)
  - Reduction in contamination or cross-over between test and control
  - Speed and confidence of experiment readouts
  - Total incremental value demonstrated by experiments

---

**45. Data-quality monitoring and schema governance for customer and event data**

**Answer Dimension (Primary):** IV - Architecture Flexibility
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** With Tealium enforcing a standardized data layer and event schema, analytics teams gain more predictable data. Validation rules and monitoring can catch missing fields, malformed values, or unexpected patterns at collection time, before they pollute downstream models and reports.

  This governance function underpins everything else: without high-quality data, segmentation, modeling, and reporting deteriorate. Tealium helps maintain that quality as the stack evolves.

- **Tealium products required:**
  - Tealium Collect - client-side schema enforcement and tag governance
  - Tealium Collect (server-side) - schema validation and monitoring for server-side events
  - Tealium Functions (optional) - corrective transformations or error routing
  - EventDB / logging - track and review data-quality issues

- **Core KPIs:**
  - Rate of schema violations / malformed events over time
  - Time to detect and fix data-quality issues
  - Reduction in downstream report/model errors caused by bad data
  - Analyst satisfaction and trust in core data sets

---

## 6. AI, Data Science & ML Engineering Teams

### Top 3 Primary Use Cases

---

**46. Foundational AI-ready behavioral data layer for model training and feature stores**

**Answer Dimension (Primary):** II - Context Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** AI models rely on high-quality, well-structured features, many of which are derived from behavioral data (page views, event funnels, recency, frequency, etc.). Tealium standardizes and enriches these signals in real time, then streams them to AI platforms and data warehouses where they can be used for feature engineering and training.

  This means AI teams don't have to build brittle, bespoke pipelines from every front-end tool. Instead, they tap into a single, governed pipeline of consented customer data, shortening time to production and improving model reliability.

- **Tealium products required:**
  - Tealium Collect - capture rich clickstream and app events
  - Tealium CDP (optional) - derived behavioral attributes (RFM, affinities)
  - Connectors to Snowflake, Databricks, BigQuery, SageMaker, etc.

- **Core KPIs:**
  - Time to stand up new AI/ML use cases (data availability)
  - Reduction in custom ETL pipelines for behavioral features
  - Model performance improvements using Tealium-sourced features
  - Data freshness/latency SLAs for AI pipelines

---

**47. Real-time AI data pipeline between Tealium and AI platforms (Snowflake, Databricks, SageMaker, etc.)**

**Answer Dimension (Primary):** II - Context Layer
**Also relevant to:** I - Real-Time Layer
**Impact:** 5/5 | **Effort:** 5/5

- **Description:** Tealium can integrate bi-directionally with cloud data and AI platforms: streaming events and profile updates in, and receiving model outputs back. This enables low-latency scoring and activation workflows where predictions are computed in or near real time and applied to active sessions or journeys.

  The architecture decouples model development from activation logic: AI teams can iterate on models without changing dozens of downstream integrations, while marketers and product teams see updated predictions flow into audiences and experiences automatically.

- **Tealium products required:**
  - Tealium Collect - real-time streaming to/from AI platforms
  - Tealium CDP - store and expose live model outputs on profiles
  - Predict ML or external ML - training, deployment, and scoring
  - Connectors to CDW/AI endpoints and activation tools

- **Core KPIs:**
  - Scoring latency (event to prediction available for activation)
  - % of key use cases using real-time vs batch AI signals
  - Business KPI lift from real-time AI vs rule-based approaches
  - Frequency/velocity of model updates with minimal activation rework

---

**48. Centralized consented data collection and filtering for AI (governed, PII-aware feeds)**

**Answer Dimension (Primary):** II - Context Layer
**Also relevant to:** IV - Architecture Flexibility
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** AI initiatives need strict control over which data is used, how PII is handled, and where consent boundaries apply. Tealium, as the consent-aware data collection and routing layer, can filter or transform events and attributes before they reach AI systems (e.g., obfuscating PII, dropping disallowed fields, segmenting by region).

  This gives AI teams a safer, compliant sandbox of data to work with while reducing the risk of shadow pipelines that bypass governance. It also simplifies auditability of which data powered which models.

- **Tealium products required:**
  - Tealium Collect - enforce collection rules and consent states
  - Tealium CDP - store consent/region attributes on profiles
  - Tealium Functions - PII obfuscation, field filtering, region-based routing
  - Connectors to AI platforms with governed feeds

- **Core KPIs:**
  - Number and severity of privacy/compliance incidents tied to AI data
  - Coverage of consent-aware enforcement across AI data feeds
  - Time to respond to DSARs or regulatory queries about AI data usage
  - Adoption of governed Tealium pipelines vs ad-hoc data feeds

---

### Remaining Use Cases

---

**49. Event-triggered model scoring workflows (propensity, risk, recommendations in real time)**

**Answer Dimension (Primary):** II - Context Layer
**Also relevant to:** I - Real-Time Layer
**Impact:** 5/5 | **Effort:** 5/5

- **Description:** Tealium can orchestrate event-driven scoring: when a user performs key actions (e.g., visits pricing, reaches a churn threshold), their recent history is sent to a model for scoring, and the returned score is attached to their profile. That score then affects routing, offers, or personalization during the same session.

  This capability unlocks real-time AI experiences such as dynamic pricing eligibility, just-in-time retention offers, or context-aware recommendations, all while keeping scoring logic decoupled from channel tools.

- **Tealium products required:**
  - Tealium Collect - event triggers and calls to model-serving endpoints
  - Tealium CDP - store event-driven scores on profiles
  - Tealium Functions - invoke external model endpoints mid-stream (Invoke Your Own Model)
  - Predict ML / external model-serving - scoring APIs
  - Connectors to CX, marketing, and personalization tools to act on scores

- **Core KPIs:**
  - Scoring turnaround time for key events
  - Performance lift for journeys using event-triggered scoring (conversion, churn)
  - Frequency and reliability of event-driven scoring calls
  - Share of journeys influenced by real-time model decisions

---

**50. AI-powered propensity and next-best-action activation across channels**

**Answer Dimension (Primary):** II - Context Layer
**Also relevant to:** III - Orchestration Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Propensity and next-best-action models often live in warehouses or model-serving layers. Tealium ingests these scores and turns them into audiences or attributes used in activation: high propensity to buy might get an offer, high propensity to churn might get a retention play, while next-best-action might determine which message or product to show.

  Because Tealium activates the same scores across email, ads, web, call center, and more, AI investments scale - each model output can influence multiple channels consistently rather than being siloed to one tool.

- **Tealium products required:**
  - Tealium Collect - ingest model outputs from CDW/AI systems
  - Tealium CDP - store propensity/NBA signals, derive segments
  - Moments API - deliver current scores and context to downstream decisioning at the moment of inference
  - Predict ML / external ML - NBA and propensity models
  - Connectors to ESP, ads, CX, decisioning engines, personalization platforms

- **Core KPIs:**
  - Incremental conversion/revenue from NBA/propensity-driven campaigns
  - Churn reduction among at-risk segments with AI-driven interventions
  - Cross-channel consistency of NBA application
  - Model utilization rate (how often scores are actually used in decisions)

---

**51. AI-powered product and content recommendation activation**

**Answer Dimension (Primary):** II - Context Layer
**Also relevant to:** III - Orchestration Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Recommendation engines - either in-house or vendor-based - generate ranked lists of products or content. Tealium can route the necessary input signals to those engines and then surface their outputs as attributes or lists in profiles, enabling activation in email, push, on-site modules, or paid media.

  This turns recommendation models into a shared service for all experience channels, rather than a one-off integration on a specific page or tool. It also supports experimentation with different recommendation strategies while keeping activation wiring stable.

- **Tealium products required:**
  - Tealium Collect - behavioral and product interaction signals
  - Tealium Functions - integration with recommendation engines
  - Tealium CDP - store recommendation lists/keys per user
  - Connectors to email, push, on-site/app personalization, and paid media

- **Core KPIs:**
  - CTR and add-to-cart for recommended items vs non-recommended
  - Cross-sell/upsell conversion and average order value uplift
  - Revenue attributed to recommendation-driven placements
  - Coverage of channels using the same recommendation logic

---

**52. AI/ML data ingestion & activation loop (closed-loop model feedback and retraining)**

**Answer Dimension (Primary):** II - Context Layer
**Impact:** 5/5 | **Effort:** 5/5

- **Description:** Tealium supports closed-loop AI workflows: events and outcomes (clicks, conversions, churn) are streamed into model training environments; models generate scores; scores are activated in real time; performance is observed and fed back into future model iterations. This loop keeps models aligned with evolving customer behavior.

  By owning the data collection and activation ends of this loop, Tealium reduces the friction AI teams face when trying to get models into production and refreshed regularly.

- **Tealium products required:**
  - Tealium Collect - bidirectional streaming between Tealium and AI/CDW
  - Tealium CDP - store model outputs and track user outcomes
  - Predict ML / external ML - training pipelines and retraining jobs
  - Connectors to activation tools and CDW for feedback data

- **Core KPIs:**
  - Model refresh frequency and ease (time from data shift to retrain)
  - Performance stability of models over time
  - Incremental value from continually improved models vs static ones
  - Number of AI/ML use cases operating in closed-loop mode

---

**53. Fraud and risk scoring activation (financial services, gaming, telco use cases)**

**Answer Dimension (Primary):** II - Context Layer
**Also relevant to:** III - Orchestration Layer
**Impact:** 5/5 | **Effort:** 5/5

- **Description:** For fraud and risk models, Tealium supplies real-time behavior and context (e.g., device patterns, geolocation, transaction anomalies) to AI systems and receives back risk scores. Those scores can gate experiences like online applications, deposits, or high-value transactions and trigger additional verification steps or manual review.

  Because Tealium also orchestrates downstream messaging, you can manage customer experience around fraud events more carefully - e.g., tailored communications when additional verification is required.

- **Tealium products required:**
  - Tealium Collect - high-fidelity behavioral and transactional events
  - Tealium Functions - integration with fraud/risk models and rules engines
  - Tealium CDP - store risk scores and flags on profiles
  - Connectors to decisioning systems, customer portals, and comms channels

- **Core KPIs:**
  - Fraud loss reduction and false positive rate for risk rules
  - Latency from risky event to decision/action
  - Customer friction metrics (e.g., additional verification rates vs approvals)
  - Net impact on revenue (blocked fraud vs friction-induced abandonment)

---

**54. PII detection, redaction, and classification workflows using AI models**

**Answer Dimension (Primary):** IV - Architecture Flexibility
**Also relevant to:** II - Context Layer
**Impact:** 4/5 | **Effort:** 4/5

- **Description:** Tealium Functions and AI integrations support workflows where text or event payloads are scanned for potential PII using AI models. Identified PII can be obfuscated, dropped, or routed differently before being stored or forwarded to tools that shouldn't receive sensitive data.

  This enables organizations to safely exploit unstructured or semi-structured data sources for AI and analytics while enforcing strong privacy and security controls at the pipeline edge.

- **Tealium products required:**
  - Tealium Collect - ingest and process raw payloads
  - Tealium Functions - call PII detection models and transform events
  - Tealium CDP (optional) - flags/metadata about PII handling
  - Connectors to downstream systems that receive sanitized data

- **Core KPIs:**
  - Detection rate and accuracy for PII in relevant payloads
  - Reduction in PII exposure in non-authorized tools/systems
  - Time to update PII rules/workflows in response to policy changes
  - Compliance/audit findings related to PII handling

---

**55. AI-enhanced call center workflows (routing, sentiment analysis, agent guidance)**

**Answer Dimension (Primary):** II - Context Layer
**Also relevant to:** III - Orchestration Layer
**Impact:** 5/5 | **Effort:** 5/5

- **Description:** By linking Tealium to call transcripts and sentiment models, organizations can capture AI-derived insights such as sentiment scores, topic classifications, or intent predictions and fold them back into customer profiles. These signals then influence routing, agent assist, and post-call journeys.

  Over time, AI-enhanced call data can also improve churn and CLV models, tying service interactions into broader predictive frameworks.

- **Tealium products required:**
  - Tealium Collect - ingest call meta and transcript outputs from CCaaS/AI
  - Tealium CDP - sentiment/intent attributes on profiles
  - Predict ML / external ML - NLP and sentiment/topic models
  - Connectors to call routing, agent assist, marketing, and CX systems

- **Core KPIs:**
  - CSAT/NPS difference when sentiment-aware flows are used
  - Churn reduction in segments with sentiment-informed interventions
  - Accuracy of sentiment/intent predictions vs human labels
  - Agent performance and handle time improvements with AI guidance

---

**56. Generative AI agents powered by Tealium profiles and events (support, sales, CX agents)**

**Answer Dimension (Primary):** II - Context Layer
**Impact:** 5/5 | **Effort:** 5/5

- **Description:** Generative AI agents - chatbots, co-pilots, or virtual assistants - are far more effective when they have structured context about the user. Tealium provides that context: who the user is, what they've done, what they own, and what their preferences are. This information can be passed as structured prompts or retrieved at runtime.

  As a result, AI agents can generate responses, suggestions, and actions that are both accurate and personalized, rather than generic. Tealium also governs which data is appropriate to share with such agents.

- **Tealium products required:**
  - Tealium CDP - user context and history attributes
  - Moments API - delivers fully assembled, governed profile context to LLM/agent platforms at the moment of inference
  - Tealium Collect - real-time events for conversational context
  - Tealium Functions - prompt/context construction and filtering
  - Connectors to LLM / agent platforms and CX surfaces (web, app, support tools)

- **Core KPIs:**
  - Resolution rate and containment for AI-driven support experiences
  - Customer satisfaction with AI agent interactions
  - Deflection of low-value contacts from human support
  - Revenue impact from gen-AI enabled sales/product guidance

---

## 7. Privacy, Compliance, and Legal Teams

### Top 3 Primary Use Cases

---

**57. Centralized consent and preference management across all channels and vendors**

**Answer Dimension (Primary):** III - Orchestration Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Tealium captures user consent states and communication preferences at points of collection - web banners, forms, preference centers - and stores them in profiles. Those states are enforced at activation time by suppressing data flows or campaigns that conflict with user choices.

  This centralization ensures that as the martech stack evolves, each new tool respects existing consent preferences without bespoke integration work. It also reduces risk of non-compliance by making consent a first-class attribute of data routing.

- **Tealium products required:**
  - Tealium Collect - consent and preference capture on web/app
  - Tealium CDP - store consent and preference attributes per profile
  - Tealium Collect (server-side) - apply consent gating to downstream event flows
  - Connectors - ensure channels and vendors receive only allowed data

- **Core KPIs:**
  - % of tools and channels honoring centralized consent states
  - Time to roll out new consent rules across the stack
  - Reduction in compliance incidents or complaints about unwanted contact
  - DSAR response speed and completeness related to consent/preferences

---

**58. Enforcement of regional data privacy rules (GDPR, CCPA, LGPD, etc.) across tools**

**Answer Dimension (Primary):** IV - Architecture Flexibility
**Also relevant to:** III - Orchestration Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Using location, residency, or organizational metadata, Tealium can classify profiles by regulatory regime and apply region-specific rules: different tags, limited data capture, or restrictions on where data is sent. These policies sit in Tealium rather than being reimplemented in every activation tool.

  Compliance teams gain assurance that geographic or legal boundaries are consistently honored, and engineering teams avoid duplicative rule management across tools and channels.

- **Tealium products required:**
  - Tealium Collect - capture region, residency, or regulatory indicators
  - Tealium CDP - store region/regulation attributes
  - Tealium Functions - apply region-specific transformations and routing
  - Connectors - vendor-level routing policies based on region

- **Core KPIs:**
  - Coverage of region-specific enforcement across all key vendors
  - Number/severity of regulatory findings tied to cross-border data misuse
  - Time to update region-based rules when laws change
  - Audit confidence in geographic data flows

---

**59. Pseudonymization, tokenization, and obfuscation of PII via Tealium Functions and flows**

**Answer Dimension (Primary):** IV - Architecture Flexibility
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Tealium Functions allow teams to run custom logic on events and attributes at collection or activation time. This can be used to hash, tokenize, or strip PII fields before they enter certain systems, helping to align data usage with privacy and security policies.

  Because these transformations happen centrally in Tealium, it's easier to audit what information is shared with which tools and to update policies as requirements change, without refactoring dozens of downstream integrations.

- **Tealium products required:**
  - Tealium Collect (server-side) - interception point for events carrying PII
  - Tealium Functions - implement pseudonymization/tokenization logic
  - Tealium CDP (optional) - track which profiles have obfuscated IDs
  - Connectors - send sanitized payloads to downstream systems

- **Core KPIs:**
  - Reduction in raw PII stored/processed in non-essential systems
  - Time and complexity of updating PII handling rules
  - Auditability of PII flows and transformations
  - Security/compliance incident rate related to exposed PII

---

### Remaining Use Cases

---

**60. Consent-aware activation and suppression (do-not-sell/share, do-not-contact, channel bans)**

**Answer Dimension (Primary):** III - Orchestration Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Do-not-contact flags, do-not-sell/share statuses, and channel-level opt-outs can be stored as Tealium attributes and used to gate activation to email, SMS, paid media, or data sharing endpoints. When consent changes, Tealium updates profiles and cascades those changes to all integrated systems via suppression or deletion signals where appropriate.

  This ensures that opt-out requests are respected globally and quickly, reducing exposure to complaints and regulatory penalties. It also simplifies supporting new regulatory requirements that introduce additional opt-out categories.

- **Tealium products required:**
  - Tealium CDP - store DNC/DNS / channel opt-out attributes
  - Tealium Collect (server-side) / Tealium Functions - enforce gating before sending events out
  - Connectors - ESP, SMS, ads, data sharing endpoints that must be suppressed
  - Tealium Collect (optional) - capture and update opt-outs in web/app interactions

- **Core KPIs:**
  - Time from opt-out action to full global enforcement
  - Number of wrongly contacted complaints after opt-outs
  - Compliance with specific opt-out categories (do-not-sell/share)
  - Reduced manual work to propagate opt-out changes across systems

---

**61. Auditability and lineage for customer data usage in marketing and AI initiatives**

**Answer Dimension (Primary):** IV - Architecture Flexibility
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** With Tealium sitting in the middle of many data flows, organizations can log what types of data were sent where, under what consent conditions, and for which use cases. This provides a clearer lineage for customer data, which is increasingly needed for AI governance, privacy impact assessments, and regulatory inquiries.

  Compliance and legal teams can use this visibility to document practices, respond to DSARs more efficiently, and support internal reviews of AI and data programs.

- **Tealium products required:**
  - Tealium Collect - capture flow-level metadata and logs
  - Tealium CDP - track consent and contextual attributes per user
  - EventDB / logging - durable audit trails of data movements
  - Connectors - instrumented with metadata to support lineage reporting

- **Core KPIs:**
  - Time to respond to regulator or auditor questions about data lineage
  - Completeness and accuracy of lineage reporting across systems
  - Number of AI/data initiatives with documented, auditable data flows
  - DSAR handling time and error rate

---

## 8. IT, Engineering, and Architecture Teams

### Top 3 Primary Use Cases

---

**62. Client-side tag management and data collection standardization with Tealium Collect**

**Answer Dimension (Primary):** IV - Architecture Flexibility
**Impact:** 5/5 | **Effort:** 3/5

- **Description:** Tealium Collect centralizes all client-side tags and pixels into a single, governed layer, with consistent load rules, data mappings, and version control. Engineering teams can manage vendor libraries and business logic once, reducing page weight, script conflicts, and ad hoc code injections.

  This makes the front-end more stable and secure while giving marketing the agility to adjust tags and tracking within controlled workflows. It also simplifies compliance by keeping a clear inventory of what scripts run and why.

- **Tealium products required:**
  - Tealium Collect - primary tag management and client-side governance
  - Tealium Collect (mobile SDK) - analogous role for native apps
  - Tealium Collect (server-side) - complementary server-side collection where desired

- **Core KPIs:**
  - Number of tags managed centrally vs hard-coded on pages
  - Page load performance, script errors, and conflicts
  - Time to deploy/update tracking for a new vendor or feature
  - Security/compliance posture regarding third-party scripts

---

**63. Server-side event collection and API hub for web, app, and backend systems**

**Answer Dimension (Primary):** IV - Architecture Flexibility
**Also relevant to:** I - Real-Time Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Tealium Collect (server-side) enables capture and routing of events without browser limitations, allowing backend systems to feed directly into the pipeline. This supports more reliable tracking (less impacted by ad blockers) and opens up sources like transactional systems, order management, or IoT devices.

  IT teams use it as a hub for real-time event distribution to analytics, CDWs, AI platforms, and activation tools, reducing point-to-point integrations and technical debt.

- **Tealium products required:**
  - Tealium Collect (server-side) - core server-side event collection and routing
  - Tealium Collect (client-side / mobile SDK) - optional companion for hybrid collection
  - Connectors to CDW/BI, AI platforms, and activation tools

- **Core KPIs:**
  - % of critical events collected server-side vs client-only
  - Resilience of tracking (less breakage from browser changes)
  - Reduction in custom integration code between systems
  - Time to onboard new event consumers (tools) using the hub

---

**64. Real-time streaming integrations into cloud data warehouses (Snowflake, Databricks, BigQuery, etc.)**

**Answer Dimension (Primary):** IV - Architecture Flexibility
**Also relevant to:** I - Real-Time Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Tealium can stream standardized, enriched customer events and profile data into data warehouses, where data teams build broader data models, dashboards, and AI workflows. Because the same schemas are used across activation and analytics, there's less work reconciling different representations of the same data.

  This turns the warehouse into a consistent system of record while still enabling low-latency activation through Tealium's real-time capabilities. It is the foundational pattern for CDP and CDW coexistence.

- **Tealium products required:**
  - Tealium Collect (server-side) - primary streaming pipeline to the warehouse
  - Tealium CDP - profile enrichment before streaming
  - Connectors to Snowflake, Databricks, BigQuery, and Redshift

- **Core KPIs:**
  - Data freshness/latency from event to warehouse availability
  - Reduction in custom ETL pipelines between collection and analytics
  - Number of warehouse-dependent analytics and AI use cases enabled
  - Consistency between CDP activation data and CDW analytical data

---

### Remaining Use Cases

---

**65. Vendor-agnostic integration layer across ESPs, DSPs, analytics, and martech tools**

**Answer Dimension (Primary):** IV - Architecture Flexibility
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Rather than wiring each system directly to every other, Tealium acts as a central integration and activation layer. Source systems (web, app, CRM, POS, etc.) send standardized data into Tealium, which then routes that data to ESPs, DSPs, analytics tools, personalization engines, and more through connectors or APIs.

  This hub-and-spoke model dramatically reduces integration complexity and fragility. It also makes it easier to add, remove, or swap vendors - data flows and activation logic remain in Tealium, while individual tools can be changed without re-plumbing the entire stack.

- **Tealium products required:**
  - Tealium Collect - ingest and route events from/to multiple systems
  - Tealium CDP - profile-based activation where needed
  - Connectors - 1,300+ pre-built vendor integrations

- **Core KPIs:**
  - Number of point-to-point integrations replaced by Tealium hub
  - Time and cost to swap or add martech vendors
  - Stability and error rates of data flows across the stack
  - IT effort saved maintaining integration complexity

---

**66. Custom data transformations and workflow logic using Tealium Functions**

**Answer Dimension (Primary):** IV - Architecture Flexibility
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** Tealium Functions gives engineers a serverless environment to write JavaScript that transforms data in motion. This includes enriching payloads with third-party data, normalizing or cleaning fields, obfuscating sensitive values, or triggering custom workflows based on complex business rules.

  These functions run inside the Tealium pipeline, so logic is centralized and version-controlled rather than scattered across separate services or client-side code. It allows IT and engineering to extend Tealium's behavior without waiting for new out-of-the-box features or connectors.

- **Tealium products required:**
  - Tealium Collect (server-side) - function execution environment for event flows
  - Tealium Functions - custom logic engine
  - Tealium CDP (optional) - store derived attributes from Functions
  - Connectors to systems that need transformed data

- **Core KPIs:**
  - Number of use cases implemented via Functions vs custom microservices
  - Time to implement or adjust transformation/business rules
  - Reduction in scattered, unversioned custom code in the stack
  - Stability and performance of function-based pipelines

---

**67. Data-quality enforcement, schema validation, and error handling at collection time**

**Answer Dimension (Primary):** IV - Architecture Flexibility
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** With a defined data layer and schema, Tealium can validate incoming events and attributes, checking for required fields, proper formats, and allowed values. When data violates expectations, Tealium can flag, correct, or block it, and route errors to monitoring systems.

  Catching quality issues close to the source reduces the cost and effort of fixing them later in the warehouse or BI tools. It also builds trust in the data that downstream teams rely on for analytics, activation, and AI.

- **Tealium products required:**
  - Tealium Collect (client-side) - client-side schema enforcement and mapping
  - Tealium Collect (server-side) - server-side schema validation, error routing
  - Tealium Functions - corrective transformations or quarantine
  - EventDB / logs - audit trail of data-quality events

- **Core KPIs:**
  - Rate of schema violations and malformed events over time
  - Mean time to detect and resolve data-quality issues
  - Reduction in downstream data incidents (broken reports/models)
  - Confidence scores or SLAs on key data sets

---

**68. Mobile SDK-based data collection and activation (in-app behavior, push, device IDs)**

**Answer Dimension (Primary):** IV - Architecture Flexibility
**Also relevant to:** I - Real-Time Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** Tealium's mobile SDK allows apps to send rich behavioral events and identifiers into the same pipeline used by web and backend systems. This includes screen views, custom events, push token registrations, and device IDs, which can be used for profile stitching and channel orchestration.

  IT and app teams gain a standardized way to instrument mobile products while marketing and analytics teams get consistent, real-time mobile data for both insight and activation. It also simplifies connecting app behavior to warehouse, analytics, and campaign tools.

- **Tealium products required:**
  - Tealium Collect (mobile SDK) - in-app tracking and ID capture
  - Tealium Collect (server-side) - relay app events to the rest of the stack
  - Tealium CDP - profile enrichment with app behavior
  - Connectors to in-app messaging, push, analytics, CDW, and marketing tools

- **Core KPIs:**
  - Coverage and quality of in-app tracking vs requirements
  - Time to instrument new app features/events
  - Stitches between app identities and web/CRM identities
  - App-related data availability in analytics and activation tools

---

**69. Event routing patterns for hybrid / warehouse-native architectures (CDP + CDW)**

**Answer Dimension (Primary):** IV - Architecture Flexibility
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** In modern architectures, organizations often combine a CDP like Tealium with a cloud data warehouse. Tealium can route raw events and curated streams into the warehouse, and also consume warehouse outputs (segments, scores) for activation.

  IT and data architecture teams use this pattern to keep storage and deep analytics in the warehouse while relying on Tealium for low-latency activation, consent-aware routing, and integration. This avoids duplication of pipelines and ensures both platforms stay in sync.

- **Tealium products required:**
  - Tealium Collect - primary pipeline to/from CDW
  - Tealium CDP - activation of CDW segments and model outputs
  - Warehouse-native Audiences - governed activation directly from warehouse-defined segments without data replication
  - Connectors to Snowflake, Databricks, BigQuery, and downstream tools
  - Tealium Functions (optional) - routing and transformation rules between layers

- **Core KPIs:**
  - Alignment between CDP and CDW datasets (consistency and latency)
  - Number of use cases that leverage both CDP activation and CDW analytics
  - Reduction in redundant ingestion/ETL pipelines
  - Time to operationalize new CDW segments/scores into activation

---

## 9. Mobile, App, and In-Product Teams

### Top 3 Primary Use Cases

---

**70. In-app behavioral tracking and profile enrichment via Tealium's mobile SDK**

**Answer Dimension (Primary):** I - Real-Time Layer
**Also relevant to:** IV - Architecture Flexibility
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** The mobile SDK captures in-app events such as screen views, feature usage, purchases, logins, and custom actions, then sends them into Tealium in real time. Those events enrich user profiles with app-specific behaviors and attributes like engagement frequency, feature adoption, or in-app purchase history.

  App teams can use this data for product analytics and for designing better onboarding, retention, and monetization experiences. Meanwhile, marketing and CX teams can include app behavior in cross-channel audiences, ensuring app activity is not siloed.

- **Tealium products required:**
  - Tealium Collect (mobile SDK) - primary in-app event collection
  - Tealium Collect (server-side) - stream app data to CDW, analytics, and activation tools
  - Tealium CDP - profile enrichment with app attributes
  - Connectors to product analytics, messaging, CDW, and marketing tools

- **Core KPIs:**
  - DAU/MAU and retention metrics with accurate app event tracking
  - Coverage of key in-app events vs tracking requirements
  - Use of app behavior in cross-channel audiences/campaigns
  - Time to instrument and deploy tracking for new app features

---

**71. In-app personalization (messages, offers, experiences) based on unified profiles**

**Answer Dimension (Primary):** II - Context Layer
**Also relevant to:** I - Real-Time Layer
**Impact:** 5/5 | **Effort:** 4/5

- **Description:** Tealium can pass audience flags and attributes (e.g., lifecycle stage, value, preferences) to in-app messaging and personalization layers. This allows app experiences to react not only to in-session behavior but also to broader cross-channel context, such as recent purchases, service interactions, or email engagement.

  As a result, app screens, in-app messages, and promos can be tailored to who the user is and what they've done elsewhere, not just what they're doing right now in the app. This creates more coherent, high-impact in-product experiences.

- **Tealium products required:**
  - Tealium Collect (mobile SDK) - in-app context and receiving personalization signals
  - Tealium CDP - segments and attributes driving in-app experiences
  - Tealium Collect (server-side) - real-time context and events to personalization backends
  - Connectors to in-app messaging/personalization SDKs and backends

- **Core KPIs:**
  - Conversion and engagement rate of personalized in-app experiences
  - Feature adoption or task completion improvements with targeted UX
  - In-app revenue uplift (IAP, upsells) from personalization
  - App retention and session frequency for personalized vs generic users

---

**72. Push notification orchestration tied to cross-channel behavior and lifecycle stage**

**Answer Dimension (Primary):** III - Orchestration Layer
**Also relevant to:** I - Real-Time Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** Push tokens collected in the app are tied to unified profiles in Tealium. Teams can then build audiences and triggers that use web, email, call center, and offline signals - not just app events - to decide when and what to push. For example, send a push only if a user hasn't opened recent emails or has abandoned a cart on web.

  This avoids overloading users with redundant notifications and aligns push within the larger lifecycle strategy. It also supports advanced patterns like escalating from email to push to SMS based on responsiveness and value.

- **Tealium products required:**
  - Tealium Collect (mobile SDK) - capture push tokens and app events
  - Tealium CDP - unified profiles, lifecycle and responsiveness attributes
  - Tealium Collect (server-side) - orchestration of triggers with other channels
  - Connectors to push providers, email/SMS, and marketing automation

- **Core KPIs:**
  - Push notification open and conversion rates
  - Cross-channel fatigue metrics (opt-outs, disablement)
  - Time-to-contact and escalation effectiveness across channels
  - Incremental revenue or retention lift from coordinated push strategies

---

### Remaining Use Cases

---

**73. App-to-web and web-to-app journey unification (deep linking and context handoff)**

**Answer Dimension (Primary):** I - Real-Time Layer
**Also relevant to:** III - Orchestration Layer
**Impact:** 4/5 | **Effort:** 3/5

- **Description:** Tealium can help tie web and app journeys together by tracking shared identifiers and campaign parameters used for deep linking. Profiles track which channel initiated a journey and maintain continuity when a user moves from email to app, app to web, or vice versa.

  This ensures attribution and behavioral context carry across environments, enabling experiences like resuming a flow in the app that was started on the web. It also improves measurement by giving a more accurate view of multi-device journeys.

- **Tealium products required:**
  - Tealium Collect (client-side and mobile SDK) - capture shared IDs and deep link params
  - Tealium CDP - cross-device profile stitching
  - Tealium Collect (server-side) - streaming events to CDW for journey analysis
  - Connectors to analytics, attribution, and personalization tools

- **Core KPIs:**
  - Cross-device stitch rate (web to app)
  - Completion rate for journeys spanning web and app
  - Attribution accuracy for deep-link driven sessions
  - Engagement or revenue lift from continuity experiences

---

**74. Mobile behavior as a signal into AI models and predictive scores**

**Answer Dimension (Primary):** II - Context Layer
**Also relevant to:** I - Real-Time Layer
**Impact:** 4/5 | **Effort:** 4/5

- **Description:** Because mobile events are normalized and streamed alongside web, CRM, and offline data, AI models can naturally incorporate app engagement as features (e.g., feature adoption, session frequency, recency). Tealium supplies this data to AI/ML environments and ingests scores back.

  App teams benefit from better predictions (e.g., churn risk or upgrade propensity that reflect in-app patterns), while activation teams can target campaigns and in-app treatments based on those more accurate signals.

- **Tealium products required:**
  - Tealium Collect (mobile SDK) - collect detailed in-app behavior
  - Tealium Collect (server-side) - stream events to AI/ML/warehouse platforms
  - Tealium CDP - store and use AI scores that incorporate mobile signals
  - Connectors to AI platforms and downstream activation tools

- **Core KPIs:**
  - Model performance uplift from including mobile features (e.g., churn, upsell)
  - Churn or upgrade rate improvement when using mobile-informed scores
  - Breadth of models and use cases that incorporate mobile data
  - Time from adding mobile features to observable business impact
