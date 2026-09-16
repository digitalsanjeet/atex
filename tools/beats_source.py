"""Source of truth for the dollar-store video visual beats.

Compact representation: each beat is (timestamp, scene_key, narration_beat).
Everything else (image prompt, negative prompt, camera, style suffix) is a
constant or derived, so the full 204-beat spec can be maintained in one place.

Run `python3 tools/build_manifest.py` to regenerate:
  - beats.json   (machine readable, full expanded image prompts)
  - prompts.md   (human readable mirror of the original spec)
"""

TITLE = "THE ECONOMICS OF OWNING A DOLLAR STORE"

STYLE_SUFFIX = (
    "Use 1\u20133 main elements with a clear visual hierarchy. "
    "Clean 2D hand-drawn editorial illustration, minimalist educational explainer artwork, "
    "white/simple background, thick black ink outlines, slightly imperfect hand-sketched linework, "
    "subtle marker texture, flat muted pastel colors, simple geometric forms, rounded cartoon characters, "
    "vector-inspired composition, educational infographic aesthetic, uncluttered, clean white space around the subject, "
    "high readability, consistent line thickness, simple shadows only, "
    "no realism, no 3D, no photorealism, no cinematic lighting, no painterly style."
)

# Locked art direction: frames carry no lettering of any kind. The narration and any
# on-screen captions are added in the edit, so artwork must stay purely visual.
TEXT_POLICY = (
    "Absolutely no text anywhere in the image: no words, letters, numbers, typography, "
    "captions, titles, headings, labels, price tags with digits, signage, storefront lettering, "
    "banners, arrows with text, speech bubbles or quote bubbles. Communicate the beat only "
    "through drawn objects, figures, gestures and simple diagrammatic shapes. Signs, "
    "awnings, product packaging, newspaper fronts and ledger pages must be blank panels or "
    "abstract horizontal strokes that suggest text from a distance, never real lettering: "
    "an empty sign panel reads correctly on screen, and the model will otherwise fill any "
    "sign-shaped region with words because that is what signs are for."
    " An invented brand name is lettering too: a plausible-sounding wordmark on a store-brand "
    "carton is as much a violation as a real one, so generic packaging stays plain colour, "
    "stripes and dots."
    " Never draw the narration's own words: when a beat contains a pithy phrase or slogan, "
    "it must not appear as a banner, poster, chalkboard or headline, because the line is sound, "
    "not signage - illustrate the idea with objects instead."
    " This ban covers proper nouns and dates in particular: a town name, a founder's name, "
    "a year or an era must never be written on a storefront, plaque, map, newspaper or "
    "caption panel - convey place and period through architecture, vehicles, clothing and "
    "props instead. The same ban covers labels the illustration invents for itself: an "
    "explanatory caption or two-word economic tag on a panel, chart or callout is the single "
    "most common violation in this project, so every panel in a diagram stays empty and the "
    "diagram must carry its meaning through shape, size, position and arrows alone. "
    "When a beat compares amounts - square footage, rent per square foot, prices, store "
    "counts - show that comparison as relative size, height or number of drawn shapes, "
    "never as digits, currency figures or tick-labelled bars."
)

# Beats name real competitors (Walmart, Target, CVS, McDonald's, Starbucks, Subway),
# so mark-free rendering is a legal requirement for a published video, not just a style
# preference. The prompt ban stills/wordmarks and asks for anonymous generic storefronts;
# the narration carries the names.
BRAND_POLICY = (
    "No brand logos, wordmarks, mascots or trademarked trade dress of any kind. When the "
    "beat mentions a named chain, represent it as a generic anonymous retail building or a "
    "neutral icon of what it sells, never its actual marks."
)

NEGATIVE_PROMPT = (
    "photorealistic, 3D render, cinematic lighting, glossy commercial photography, clutter, "
    "excessive detail, realistic faces, text-heavy infographic, watermark, logo, "
    "text, letters, words, numbers, typography, captions, subtitles, signage, lettering, "
    "price tags with digits, speech bubbles, brand logo, wordmark, trademark, "
    "mascot, trade dress"
)

CAMERA = (
    "Medium-wide editorial framing, eye-level, slight three-quarter perspective, "
    "clear subject separation, static composition suitable for subtle documentary motion."
)

# Appended last so every render is composed for a 16:9 video frame.
FRAMING = "Wide 16:9 landscape frame, horizontal composition."

# Guards against the sparse-subject failure mode: "lots of negative space" can be read
# as "make everything tiny", which fails at 1080p under a slow push-in.
SCALE = (
    "Composition rule, mandatory: the single main subject must be LARGE, occupying 55\u201375% "
    "of the frame height on its own, drawn at close working distance so it stays crisp and "
    "readable at 1080p and survives a slow push-in. Any secondary elements are clearly smaller "
    "and sit to the sides. Never shrink the subject into a small vignette floating in a large "
    "empty white field, and never spread the scene out as many tiny distant objects. Equally, "
    "keep the white ground visible as breathing room: do not let the artwork fill the frame "
    "edge to edge or run colour across the whole background. "
    "When the narration implies many locations or countless units, do NOT tile repeated "
    "copies of the same building or object across the frame to convey quantity: draw one "
    "dominant subject and imply scale with a single clearly smaller secondary element."
)

SCENES = {
    "storefront": "Create clear American dollar-store scene illustrating the narration beat.",
    "small_town": "Create small-town comparison between a dollar store and a closing independent grocery store.",
    "economics": "Create simple dollar-store economics scene with shelves, cash, rent, payroll and delivery boxes.",
    "fill_in": "Create shopper making a quick small fill-in purchase with a few everyday essentials.",
    "rural_map": "Create rural American community map with a nearby dollar store and distant major retailer. Keep the map a small backdrop; one large store or figure must dominate the frame.",
    "five_and_dime": "Create historical American five-and-dime or 1950s dollar-store scene.",
    "chains_map": "Create small dollar store contrasted with large retail chains on a simple American map. Keep the map a small backdrop; one large store or figure must dominate the frame.",
    "pack_sizes": "Create side-by-side dollar-store and grocery-store packages showing different sizes.",
    "price_choice": "Create shopper choosing between a low dollar-store price and a higher retail price.",
    "safety": "Create dollar-store interior showing understaffing and an editorially clear safety issue.",
    "supply_chain": "Create centralized dollar-store corporate supply chain connecting warehouse, suppliers and stores.",
    "downturn": "Create American economic downturn scene with shoppers moving toward a low-price dollar store.",
    "zoning": "Create town planning map showing zoning boundaries and concentrated dollar-store locations.",
}

# (timestamp, scene_key, narration beat)
BEATS = [
    ("00-00", "storefront", "There's one on almost every corner in America, in small towns, in strip malls, in"),
    ("00-06", "small_town", "neighborhoods where the grocery store closed years ago. You've probably walked"),
    ("00-10", "storefront", "into one, picked up a few things, and walked out spending less than ten"),
    ("00-14", "economics", "dollars. Simple, cheap, convenient. But here's what almost nobody asks while"),
    ("00-20", "fill_in", "they're standing in that fluorescent lit aisle, tossing a bottle of dish soap into"),
    ("00-24", "economics", "their basket. How does this store make any money? Everything costs a dollar or"),
    ("00-29", "economics", "close to it. The margins must be razor-thin. The rent still has to be"),
    ("00-34", "economics", "paid. The employees still need paychecks. The trucks still have to show up every"),
    ("00-39", "economics", "week. So how does a store that sells everything for one dollar, or close to"),
    ("00-44", "economics", "one dollar, turn into one of the most dominant retail forces in the history of"),
    ("00-48", "storefront", "American commerce? That question has a very specific answer. And once you"),
    ("00-53", "economics", "understand it, you'll never look at a dollar store the same way again. Let's"),
    ("00-57", "economics", "start with what most people assume. They assume dollar stores are for people who"),
    ("01-01", "storefront", "can't afford to shop anywhere else. They assume the products are low quality. They"),
    ("01-06", "storefront", "assume the business model is simple. Buy cheap, sell cheap, hope enough people show"),
    ("01-11", "storefront", "up. That assumption misses almost everything about how this industry"),
    ("01-15", "economics", "actually operates. Because the dollar store business, at its most evolved form,"),
    ("01-21", "rural_map", "isn't really selling products. It's selling access. Access to household"),
    ("01-25", "storefront", "essentials in the places where no one else will go. And that positioning, quiet,"),
    ("01-30", "storefront", "unglamorous, almost invisible, is exactly what makes it so extraordinarily"),
    ("01-35", "economics", "powerful. To understand why, you have to understand where dollar stores came from."),
    ("01-41", "five_and_dime", "The concept traces back to the five-and-dime stores of the early 20th"),
    ("01-45", "five_and_dime", "century. Woolworths, the great-grandfather of them all, built an"),
    ("01-49", "economics", "empire on the idea that fixed low prices could drive enormous volume. You didn't"),
    ("01-54", "storefront", "have to negotiate. You didn't have to wonder if you were getting a good deal."),
    ("01-58", "economics", "Everything was the same price. That simplicity was the product. But the"),
    ("02-03", "economics", "modern dollar store as we know it really took shape in the 1950s and 1960s when a"),
    ("02-09", "five_and_dime", "man named Cal Turner Sr. opened the first Dollar General store in"),
    ("02-13", "five_and_dime", "Scottsville, Kentucky, in 1955. The idea was straightforward. Every item in the"),
    ("02-19", "five_and_dime", "store would cost one dollar or less. Cal Turner understood something that most"),
    ("02-23", "chains_map", "retailers didn't. There was an enormous population of Americans who were being"),
    ("02-28", "storefront", "underserved. Not just poor. Underserved. People who lived far from major"),
    ("02-33", "chains_map", "retailers. People who didn't have reliable transportation. People for whom a trip to"),
    ("02-38", "chains_map", "Walmart 20 miles away wasn't a casual errand. These people needed basic goods."),
    ("02-43", "economics", "They needed them nearby. And they needed them at prices they could manage. That"),
    ("02-48", "rural_map", "insight, that geography and accessibility matter as much as price, became the"),
    ("02-53", "storefront", "foundation of everything that followed. Fast forward to today and the numbers"),
    ("02-57", "economics", "are staggering. Dollar General alone operates more than 19,000 stores across"),
    ("03-03", "economics", "the United States. Dollar Tree, which acquired Family Dollar in 2015, operates"),
    ("03-09", "storefront", "another 16,000 locations. Combined, these two companies operate more retail"),
    ("03-14", "chains_map", "locations in America than McDonald's and Starbucks put together. Let that land for"),
    ("03-19", "chains_map", "a moment. More locations than McDonald's and Starbucks combined. And most people"),
    ("03-24", "storefront", "couldn't tell you the name of either company's CEO. This is what makes the"),
    ("03-29", "economics", "dollar store industry so fascinating. It is enormous, dominant and almost entirely"),
    ("03-34", "economics", "invisible to the people who don't depend on it. The customers who use dollar"),
    ("03-39", "rural_map", "stores most heavily, lower-income households, rural communities, people in"),
    ("03-44", "rural_map", "what are called food deserts, are not the people writing business coverage in"),
    ("03-47", "economics", "major newspapers. So the story of how dollar stores actually work has largely"),
    ("03-52", "storefront", "gone untold. Let's tell it now. The first thing to understand is the real estate"),
    ("03-58", "economics", "strategy. This is where the dollar store business model begins. Not with the"),
    ("04-02", "economics", "products. Not with the pricing. With the land. Dollar General has been"),
    ("04-07", "chains_map", "extraordinarily disciplined about where it puts its stores. The company targets"),
    ("04-11", "storefront", "communities with populations between 520,000 people. Small towns, suburban"),
    ("04-17", "chains_map", "edges, rural counties. Places that major retailers like Walmart and Target have"),
    ("04-22", "storefront", "looked at and decided aren't worth the investment. And here's the key insight"),
    ("04-27", "storefront", "about those locations. The real estate is cheap. Dramatically cheaper than urban or"),
    ("04-32", "economics", "suburban retail space. A Dollar General store typically occupies somewhere"),
    ("04-37", "storefront", "between seven and ten thousand square feet. In a small town in Tennessee or"),
    ("04-41", "rural_map", "rural Georgia, that space might rent for five to eight dollars per square foot"),
    ("04-46", "storefront", "per year. Compare that to a retail space in a mid-sized city, which might cost 25"),
    ("04-51", "economics", "to 40 dollars per square foot. The cost structure is fundamentally different."),
    ("04-57", "economics", "Dollar stores are operating in markets where their overhead is a fraction of"),
    ("05-00", "storefront", "what it would be anywhere else. And because they're the only significant"),
    ("05-04", "chains_map", "retailer within miles in many of these communities, they don't have to compete"),
    ("05-08", "chains_map", "on price with anyone nearby. They don't have competition. They are the market. Now"),
    ("05-14", "storefront", "let's talk about what's actually inside the store. Because this is where the"),
    ("05-18", "storefront", "business model gets genuinely sophisticated. Most people assume that if"),
    ("05-22", "economics", "something costs a dollar, the store barely makes any money on it. That"),
    ("05-26", "economics", "assumption is wrong. Dollar stores have become extraordinarily skilled at what's"),
    ("05-31", "pack_sizes", "called shrinkflation and pack size manipulation. The products on the shelves"),
    ("05-35", "small_town", "of a dollar store are not always the same products you find at a grocery store"),
    ("05-39", "chains_map", "or a big-box retailer. They are specifically manufactured versions,"),
    ("05-44", "economics", "smaller quantities, different package sizes. A bottle of detergent at a dollar"),
    ("05-49", "pack_sizes", "store might contain 20 ounces instead of 32. A package of cookies might have 12"),
    ("05-54", "pack_sizes", "instead of 18. The price point stays low. The quantity quietly shrinks. The margin"),
    ("06-00", "economics", "expands. This is not accidental. Dollar stores work directly with manufacturers"),
    ("06-05", "economics", "to create store-specific package sizes that maintain the low price point while"),
    ("06-10", "economics", "protecting the margin. The consumer sees a familiar brand at a price they can"),
    ("06-14", "storefront", "afford. The manufacturer gets a distribution channel into a massive"),
    ("06-18", "economics", "customer base. The dollar store captures a margin that looks impossible from the"),
    ("06-23", "storefront", "outside, but is completely engineered from the inside. And what are those"),
    ("06-27", "economics", "margins? The gross margin on a typical dollar store item runs somewhere between"),
    ("06-32", "storefront", "30 and 35 percent. That's competitive with, and in many cases better than,"),
    ("06-37", "small_town", "traditional grocery stores, which often run margins in the mid-twenties. The"),
    ("06-41", "economics", "dollar store is not a low margin business. It is a precisely engineered"),
    ("06-45", "economics", "margin business disguised as a low margin business. Now let's layer in the"),
    ("06-50", "price_choice", "psychology, because this is where the dollar store becomes truly fascinating."),
    ("06-55", "price_choice", "There is a powerful psychological phenomenon called price anchoring. When"),
    ("07-00", "economics", "you walk into a dollar store and see that everything costs one dollar or close"),
    ("07-04", "price_choice", "to one dollar, your brain calibrates its sense of value against that anchor. A"),
    ("07-09", "economics", "bottle of shampoo that costs four dollars at CVS feels expensive. The same"),
    ("07-14", "price_choice", "functional product at a dollar store feels like a bargain, even if the per"),
    ("07-19", "price_choice", "ounce cost is actually higher. Your brain is not calculating unit economics. Your"),
    ("07-24", "price_choice", "brain is responding to the price tag. One dollar feels good. One dollar feels like"),
    ("07-29", "price_choice", "you are winning. This psychological effect is so powerful that dollar stores"),
    ("07-34", "small_town", "can charge more per unit than grocery stores, while making their customers feel"),
    ("07-38", "price_choice", "like they're saving money. It is one of the most elegant pricing tricks in all"),
    ("07-42", "economics", "of retail, and it works particularly well on a specific type of purchase. Dollar"),
    ("07-47", "chains_map", "stores generate a significant portion of their revenue from what retailers call"),
    ("07-51", "fill_in", "fill-in shopping. You're not doing your weekly groceries at a dollar store. You"),
    ("07-56", "fill_in", "ran out of dish soap. You need a birthday card. You want a bag of chips and a soda."),
    ("08-01", "storefront", "The basket size is small. The transaction is quick, and because the"),
    ("08-05", "economics", "anchored price feels low, you don't compare it to alternatives. You just buy."),
    ("08-10", "chains_map", "This is why dollar stores are not actually competing with Walmart. They are"),
    ("08-14", "chains_map", "competing with convenience stores, and they are winning that competition"),
    ("08-18", "storefront", "decisively. Let's talk about the operational model, because this is where"),
    ("08-23", "economics", "the cost structure becomes remarkable. A typical dollar general store operates"),
    ("08-27", "economics", "with somewhere between five and ten employees, often fewer. The stores are"),
    ("08-32", "storefront", "deliberately designed to require minimal labor. Fixtures are simple. Products are"),
    ("08-38", "storefront", "often sold directly from the shipping boxes they arrived in, stacked on low"),
    ("08-42", "storefront", "shelves that customers can reach themselves. There is no deli counter, no"),
    ("08-47", "small_town", "fresh produce section that requires constant rotation and maintenance, no hot"),
    ("08-52", "storefront", "food program, no specialty departments. The simplicity is engineered. Every"),
    ("08-57", "storefront", "element of the store design is optimized to reduce labor hours, because labor is"),
    ("09-02", "economics", "one of the largest costs in retail, and dollar stores have figured out how to"),
    ("09-07", "economics", "run a profitable retail operation with a skeleton crew. That stripped-down model"),
    ("09-11", "economics", "creates an interesting tension. Dollar General has faced significant criticism"),
    ("09-16", "safety", "and regulatory scrutiny for understaffing. Workers report being alone in stores for"),
    ("09-21", "safety", "hours. Safety inspections have found blocked fire exits, unstable merchandise"),
    ("09-26", "safety", "stacks, and conditions that regulators have called hazardous. The Occupational"),
    ("09-31", "safety", "Safety and Health Administration has cited Dollar General hundreds of times"),
    ("09-35", "chains_map", "in recent years, making it one of the most cited retailers in the country. This"),
    ("09-40", "storefront", "is the shadow side of the lean operating model. The efficiency that makes the"),
    ("09-44", "economics", "business so profitable creates working conditions that have drawn serious"),
    ("09-48", "safety", "criticism from regulators, labor advocates, and the communities these"),
    ("09-52", "storefront", "stores are supposed to serve. But the financial performance remains"),
    ("09-55", "economics", "extraordinary. Dollar General's annual revenue has exceeded 37 billion dollars"),
    ("10-01", "storefront", "in recent years. The company serves more than 90 million unique customers per year."),
    ("10-06", "storefront", "It opens approximately 800 new stores every single year. That is more than two"),
    ("10-12", "storefront", "new stores every single day, 365 days a year, year after year. Think about"),
    ("10-18", "economics", "what that means operationally. Dollar General has built a machine that can"),
    ("10-22", "storefront", "identify a location, negotiate a lease, build out a store, stock it, hire staff,"),
    ("10-28", "storefront", "and open for business at a rate of more than two locations per day. That kind of"),
    ("10-33", "storefront", "execution at that kind of scale is genuinely extraordinary, regardless of"),
    ("10-38", "supply_chain", "what you think about the business. Now let's talk about the franchise question,"),
    ("10-42", "supply_chain", "because this surprises almost everyone. Dollar General does not franchise. Dollar"),
    ("10-48", "chains_map", "Tree does not franchise. These are not franchise operations like McDonald's or"),
    ("10-53", "storefront", "Subway where individual owners pay fees to operate under the brand. These are"),
    ("10-58", "supply_chain", "company-owned chains. Every Dollar General you've ever walked into is owned"),
    ("11-02", "supply_chain", "and operated by Dollar General Corporation. The implication is"),
    ("11-05", "economics", "significant. The profits from 19,000 stores flow back to one company. The real"),
    ("11-11", "supply_chain", "estate decisions are made centrally. The supply chain is controlled end-to-end."),
    ("11-16", "supply_chain", "The leverage with suppliers is enormous, because when you're buying for 19,000"),
    ("11-20", "supply_chain", "locations simultaneously, you dictate terms. And that supply chain leverage is"),
    ("11-26", "economics", "a crucial piece of the puzzle. Dollar stores buy in volumes that give them"),
    ("11-30", "supply_chain", "extraordinary power over their suppliers. They can negotiate prices, package sizes,"),
    ("11-35", "chains_map", "and delivery schedules that smaller retailers could never achieve. They use"),
    ("11-39", "supply_chain", "private label products, store-branded goods that carry even higher margins than"),
    ("11-44", "storefront", "national brands, to fill key categories where the economics work especially well."),
    ("11-49", "supply_chain", "Dollar Tree's private label penetration has grown significantly in recent years."),
    ("11-53", "economics", "When you buy a cleaning product with a Dollar Tree label instead of a brand"),
    ("11-56", "economics", "name, the store is capturing the entire margin that would otherwise be shared"),
    ("12-00", "storefront", "with the manufacturer. It is one of the highest leverage moves in retail. Let's"),
    ("12-05", "economics", "zoom out and look at the macro picture, because what dollar stores reveal about"),
    ("12-09", "economics", "America is as interesting as the business model itself. The dollar store"),
    ("12-13", "downturn", "industry has grown fastest during economic downturns. During the 2008"),
    ("12-18", "downturn", "financial crisis, dollar store revenues accelerated sharply. During the COVID"),
    ("12-23", "downturn", "pandemic, dollar stores were designated essential businesses and stayed open"),
    ("12-28", "chains_map", "while other retailers closed. During every period of economic stress in recent"),
    ("12-32", "economics", "American history, dollar stores have gotten stronger. This counter cyclical"),
    ("12-37", "economics", "resilience is built into the business model by design. Dollar stores serve"),
    ("12-41", "rural_map", "customers who are already buying at the lowest accessible price point. When the"),
    ("12-46", "downturn", "economy gets worse, more customers trade down to that price point from higher-end"),
    ("12-51", "chains_map", "retailers. The customer base expands in hard times. This is the opposite of most"),
    ("12-56", "storefront", "retail businesses, which contract when consumers tighten spending. And there's a"),
    ("13-02", "rural_map", "longer-term demographic story here too. Food deserts, areas where residents have"),
    ("13-07", "rural_map", "limited access to affordable, nutritious food, are a significant and growing"),
    ("13-11", "storefront", "problem in the United States. The USDA estimates that tens of millions of"),
    ("13-16", "rural_map", "Americans live in food deserts. In many of those communities, the dollar store is"),
    ("13-21", "economics", "the only food retail option available. Dollar stores have become de facto"),
    ("13-25", "small_town", "grocery stores for millions of Americans who have no alternative. Critics argue"),
    ("13-30", "rural_map", "that dollar stores actually make food deserts worse by crowding out independent"),
    ("13-34", "chains_map", "grocery stores and fresh food retailers. When a dollar store opens in a small"),
    ("13-39", "small_town", "town, a local grocery store often closes within a few years. The community ends up"),
    ("13-44", "rural_map", "with access to processed food and household goods, but loses access to"),
    ("13-49", "small_town", "fresh produce. This creates a genuine tension between the business's success"),
    ("13-53", "storefront", "and the well-being of the communities it serves. Some cities and counties have"),
    ("13-58", "zoning", "actually tried to limit dollar store expansion. Tulsa, Oklahoma and Mesquite,"),
    ("14-02", "chains_map", "Texas have implemented zoning restrictions specifically targeting"),
    ("14-06", "zoning", "dollar store density. They've argued that concentrating too many dollar stores in"),
    ("14-11", "small_town", "a neighborhood creates a retail monoculture that undermines community"),
    ("14-15", "rural_map", "food access. It's a rare example of local government pushing back against a"),
    ("14-20", "storefront", "business that its residents are actively choosing to patronize. That tension"),
    ("14-25", "small_town", "between individual choice and community impact is one of the most interesting"),
    ("14-30", "economics", "aspects of the dollar store story. People choose to shop there, the stores serve a"),
    ("14-35", "storefront", "genuine need, and at the same time the cumulative effect of their expansion has"),
    ("14-40", "storefront", "consequences that individual shoppers aren't weighing when they walk in to buy"),
    ("14-44", "fill_in", "dish soap. Now let's bring this all the way back to the original question. How"),
    ("14-49", "economics", "does a store that sells everything for a dollar or close to a dollar turn into one"),
    ("14-54", "economics", "of the most powerful retail forces in America? The answer is not the price. The"),
    ("14-59", "economics", "price is the hook, the thing that draws you in and makes you feel good about"),
    ("15-04", "rural_map", "being there. The real answer is geography. Dollar stores went where no one else"),
    ("15-09", "chains_map", "would go. They planted themselves in the spaces between the big retailers. They"),
    ("15-14", "chains_map", "serve the customers that Walmart and Target and grocery chains decided weren't"),
    ("15-18", "storefront", "worth the investment. And in doing so, they didn't just build stores, they built"),
    ("15-23", "chains_map", "captive markets. When you are the only retailer within 15 miles, you don't need"),
    ("15-29", "economics", "to have the best prices, you don't need the widest selection. You just need to"),
    ("15-33", "economics", "be there. And dollar stores have turned being there consistently, reliably, at"),
    ("15-39", "economics", "scale, into a $37 billion empire. The dollar sign on that storefront isn't just"),
    ("15-45", "economics", "a price, it's a promise. A promise that says no matter where you live, no matter"),
    ("15-51", "storefront", "how much you make, there is a place that will sell you what you need. Whether that"),
    ("15-55", "economics", "promise is entirely kept, whether what dollar stores provide is really what"),
    ("15-59", "storefront", "those communities need, is a question the industry is still answering. But the"),
    ("16-04", "storefront", "business? The business works. Brilliantly. Quietly. In places most people never"),
    ("16-10", "storefront", "think about. Which is exactly why almost nobody sees it coming."),
]


def build_beats():
    """Expand the compact table into full beat records."""
    records = []
    for timestamp, scene_key, beat in BEATS:
        scene = SCENES[scene_key]
        prompt = (
            f"{scene} Visually communicate this narration beat: \u201c{beat}\u201d "
            f"{TEXT_POLICY} {BRAND_POLICY} {STYLE_SUFFIX} "
            f"Negative prompt: {NEGATIVE_PROMPT}. "
            f"{CAMERA} {SCALE} {FRAMING}"
        )
        records.append(
            {
                "timestamp": timestamp,
                "seconds": int(timestamp.split("-")[0]) * 60 + int(timestamp.split("-")[1]),
                "file": f"{timestamp}.png",
                "scene": scene_key,
                "narration_beat": beat,
                "image_prompt": prompt,
                "negative_prompt": NEGATIVE_PROMPT,
                "camera": CAMERA,
            }
        )
    return records


if __name__ == "__main__":
    print(len(BEATS), "beats")
