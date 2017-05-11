# <center>Ax/Wx - Traffic Accident / Weather Analysis</center>
# <center>Functional Specification</center>


BACKGROUND
----------
_What problem you're trying to solve. Why it's important. How your users will benefit._

Unfortunately, traffic collisions are a part of everyday life in Washington State, and it is in the interest of the public to try to cut down on the number of collisions. A first step towards limiting the number of collisions is understanding what factors are to blame. To this end, the Washington State Patrol (WSP) maintains a detailed database of collisions.

One of the major contributors to collisions is the weather, even if it is not the primary cause of the collision itself. The WSP database records the weather conditions at the time of the collision per the reporting officer on the scene. While this provides beneficial insight into the weather, these observations are often made ad-hoc or after the fact by non-weather professionals. These observations are subjective and not corroborated by an alternate reputable source, which may not always paint a full (or accurate) picture of what was happening in the moments leading up to a collision. High quality objective weather data exists at airports and several other official locations, however, these locations are quite sparse and often fail to capture the small-scale weather features that can contribute to collisions.

Weather Underground (WU) hosts a Personal Weather Station (PWS) network with over 4,200+ stations in Washington. These stations, while not guaranteed to be as accurate as official reporting stations, are much more widespread offering greater coverage of objective weather data than the ‘official’ reporting stations. It is possible that these stations can be leveraged to provide objective historical observations of the conditions in the vicinity and in the moments leading up to individual collisions.

We aim to create a tool to integrate WSP collision data and WU weather data. The tool will allow users to explore the relationship between certain weather conditions and collision frequency, type, and severity. It would include the ability to identify locations that are prone to collisions during certain conditions based on the historical data, with a goal of improving road safety through more informed decision making. Additionally, the tool could provide real-time predictions about which locations have a higher-than-normal risk for traffic collisions using current conditions.


USERS
-----
_Who will use your system? What level of computer experience do they require? What domain knowledge must they have?_

Our target users are individuals in positions of authority to act on the information provided by the visualization tool to make roads safer.  Primarily, we are targeting the following user types:

#### Traffic Engineer

To use this visualization tool, the level of computer experience required for a traffic engineer is familiarity with operating graphical user interfaces (point, click, drag, apply drop-down filters). The domain knowledge required to make proper use of the visualization tool will need to be on an expert level regarding high-level understanding of traffic planning, specifically to the Seattle area. A traffic engineer would be able to utilize this resource to identify recurring issues in traffic frequency due to inclement weather and make informed daily decisions as to whether precautionary signs or crash barriers may be required in short-term tactical planning.  For long-term strategic planning, they can assess frequencies and severity of collisions based on location to make proposals for infrastructure improvements to city officials.

##### Law Enforcement Officer

The level of computer experience required for a law enforcement officer to use this tool is familiarity with operating graphical user interfaces. For domain experience, a law enforcement officer will need to have practical knowledge and hands-on experience encountering automobile collisions in the Seattle area. With this tool, they can better plan their daily shifts given knowledge of recurring locations of collisions. This may result in an increased visual presence for a specific location that is known to be hazardous, or other proactive safety measures.

#### Insurance Company

To use this visualization too, the level of computer experience required for an individual working for an insurance company is familiarity with graphical user interfaces. The required domain experience would be assessing risk and setting policy premiums based off the risk and occurrences of collisions in the region with the added component of weather effects (actuarial/underwriting).

#### Common Driver
 
The level of computer experience required for a common driver living in Seattle to use this tool is familiarity with graphical user interfaces. The domain experience required would be standard driving experience and knowledge of geographic locations of roads/highways in the Seattle area. The common driver would be able to benefit from this tool through additional information that can be utilized for trip planning in the case of inclement weather conditions.


USE CASES
---------
_Use cases. How will users interact with the system and how will the system respond. You likely want to have "mock ups" of screenshots and indicate how users will interact._

#### Traffic Engineer

Traffic engineers already know to some degree where and when traffic is heavy and make infrastructural improvements by creating new roadways, expanding or changing existing roadways, and monitoring the flow of traffic. The flow of traffic in Seattle can be explained by traffic engineers through observations of multiple variables. With a tool that provides more in depth analysis of traffic related directly to weather patterns, it may be possible for traffic engineers to further “curb” the increased traffic flow by taking countermeasures during times of weather that are known to impact traffic with a high probability. Recently in Seattle, traffic engineers have implemented “variable speed zones” on I-5 based on traffic patterns. A traffic engineer could use the predictive analysis of Ax/Wx to determine where more “variable speed zones” should be implemented, and when the speed should be adjusted (i.e. collisions occur X% more often at location Y when the weather conditions are Z).

<center>_(Insert Use Case Picture Here)_</center>

#### Law Enforcement Officer

Law enforcement officers would interact with this tool by understanding where collisions were likely to happen when certain weather conditions rolled in. The tool will take all the collision information and combine it with detailed weather data for that time. A statistical model will be built from this data and used to predict where the location of highest probability for collisions will occur based on the current weather conditions. An officer would then have a map of Seattle showing them where those areas would be and be able to potentially stop collisions before they happen. Simple being visually present at a given location reduces the speed of traffic and forces drivers to be more self-aware. Weather is not necessarily the sole cause of collisions, but rather a contributing factor, along with many others including speed. Unfortunately, we cannot control the weather, but we do have the ability to adjust other factors that may be amplified by the weather conditions. A law enforcement officer could look at the weather report prior to planning his or her shift, and subsequently use the Ax/Wx tool to determine where collisions are more likely to occur given the current weather (predictive analysis based on past conditions). Providing an increased law enforcement presence in those specific locations may reduce collisions.

<center>_(Insert Use Case Picture Here)_</center>
<center>_Have a google map with ‘hot zones’ of high probability_</center>
<cneter>_traffic collisions based on current weather conditions._</cneter>

#### Insurance Company

Although it is recognized that the use of Ax/Wx by insurance companies may negatively impact drivers through increased premiums, it may also benefit other drivers through decreased premiums. Insurance companies already look at the distances driven by insured drivers, but with the increasing number of vehicles that have GPS built-in they could begin tracking where and when insured drivers are driving. With Ax/Wx an individual working for an insurance company could determine whether an insured driver drives frequently in areas known to have an increased risk of collisions due to inclement weather conditions. Alternatively, they could also use Ax/Wx to reduce premiums for drivers that drive more often in fair weather or along roadways that are not significantly impacted by weather conditions. Another use case for an individual working for an insurance company would be to provide coverage to drivers at different rates throughout shorter time periods (i.e. winter premiums versus summer premiums). Some drivers may benefit from this as they may only be seasonal employees and drive during the summer months only.

<cneter>_(Insert Use Case Picture Here)_</cneter>

#### Common Driver

While it may not be as financially impactful for common drivers or pertain to a larger goal such as making decisions to increase overall traffic safety, Ax/Wx would still be available to everyone. Like the use of Google Maps (or some other GPS app), Ax/Wx could potentially provide drivers with the best route possible for avoiding traffic collisions (based on historical data), given the current weather conditions. Ideally, this would be in some form of a mobile app and even more ideally, integrated with an existing app to provide more real-time information while a person is driving. Currently, the common driver could still use Ax/Wx to plan a road trip given the weather forecast.

<center>_(Insert Use Case Picture Here)_</center>

#### MOCK UP OF COLLISION MAP

#### MOCK UP OF WEATHER STATION MAP

#### MOCK UP OF PREDICTIVE COLLISION MAP BASED ON THE WEATHER

#### EXTRA STUFF AND TEXT TIDBITS:

To this end, the Washington Traffic Safety Committee aims to end traffic deaths and serious injuries in the state by 2030(1).
