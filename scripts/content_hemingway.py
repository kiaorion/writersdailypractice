#!/usr/bin/env python3
"""Hemingway long-tail sub-page batch (first proof batch). Run: python scripts/content_hemingway.py"""
from gen_subpage import build

A = "ernest-hemingway"
AN = "Ernest Hemingway"
DATE_ISO = "2026-06-28"
DATE_DISP = "June 28, 2026"
BLURB = "His first-light schedule, the standing desk in Cuba, the pencils, the chart on the wall, and the discipline behind the simple prose."

FULL_LINE = {"p": f"For the complete picture of how Hemingway worked, including his desk, his pencils, his revision habits, and the famous theory of omission, see the full <a href='/writers-routines/{A}/'>Ernest Hemingway writing routine page</a>."}

PAGES = [
    {
        "author_slug": A, "author_name": AN, "subslug": "word-count",
        "date_iso": DATE_ISO, "date_disp": DATE_DISP, "read_time": 5,
        "crumb": "Word Count",
        "title": "How Many Words Did Ernest Hemingway Write a Day? | The 500-Word Answer",
        "meta_desc": "Ernest Hemingway averaged about 500 words a day and tracked every session on a cardboard chart. Here's the real number, where it comes from, and why he kept it low.",
        "og_title": "How Many Words Did Ernest Hemingway Write a Day?",
        "og_desc": "Around 500 words a day, tracked on a chart so he couldn't kid himself. Here's the full story behind Hemingway's word count.",
        "tw_desc": "About 500 words a day, logged on a cardboard chart. Here's why Hemingway kept the number deliberately small.",
        "h1": "How Many Words Did Ernest Hemingway Write a Day?",
        "intro": "The number most often quoted is 500 words a day, and that's close to right. But Hemingway's word count is more interesting than a single figure, because he tracked it obsessively and kept it deliberately low for a reason most writers get backwards.",
        "answer": "About 500 words per day, on average.",
        "answer_sub": "Hemingway logged his daily output on a hand-drawn chart to keep himself honest. Counts ran from roughly 450 on a normal day to over 1,000 when he wanted to earn a day of fishing. He wrote in the morning and stopped while it was still going well.",
        "blocks": [
            {"h2": "The Chart on the Wall"},
            {"p": "We know Hemingway's numbers because he wrote them down. In his 1958 <em>Paris Review</em> interview, George Plimpton described a large chart Hemingway kept, made from the side of a cardboard packing box and propped against the wall of his home in Cuba. On it, Hemingway recorded the word count of each day's work. His stated reason was blunt: he did it \"so as not to kid myself.\""},
            {"p": "The figures Plimpton copied down tell the story better than any average. They ran 450, 575, 462, 1250, then back to 512. The normal day landed somewhere near 500. The big days, the ones over a thousand, weren't breakthroughs. They were Hemingway banking extra words so he wouldn't feel guilty taking the next day off to fish the Gulf Stream."},
            {"h2": "Why 500 and Not 2,000"},
            {"p": "Five hundred words is a small day. Stephen King aims for <a href='/writers-routines/stephen-king/word-count/'>2,000</a>. Anthony Trollope cleared 3,000 before breakfast. So why did one of the most productive novelists of the century cap himself so low?"},
            {"p": "Because Hemingway wasn't optimizing for words per day. He was optimizing for words per year, and for the quality of the next morning. His whole method depended on never draining the tank. If he wrote until he had nothing left, he would sit down the next day facing emptiness. By stopping near 500, while he still knew what came next, he protected tomorrow's session. The low number was the point, not a limitation."},
            {"p": "It also reflects how he wrote. Hemingway revised as he went and chose words with a jeweler's patience. His prose is famous for what it leaves out. Five hundred of his words could carry the freight of two thousand of someone else's."},
            {"quote": "I had learned already never to empty the well of my writing, but always to stop when there was still something there in the deep part of the well, and let it refill at night from the springs that fed it.", "by": "Ernest Hemingway, <em>A Moveable Feast</em>"},
            FULL_LINE,
            {"h2": "What You Can Steal"},
            {"ul": [
                "<strong>Count your words, but don't worship the count.</strong> Hemingway tracked his to stay honest, not to win a race. A visible daily number is a quiet form of accountability.",
                "<strong>Pick a target you can hit on a bad day.</strong> Five hundred words is reachable when you're tired, sick, or flat. A target you actually hit beats an ambitious one you abandon.",
                "<strong>Bank ahead when it flows.</strong> On good days, push past the target so a future day off costs you neither guilt nor momentum.",
                "<strong>Stop before you're empty.</strong> The whole reason for a small number is that you finish with fuel left for tomorrow.",
            ]},
        ],
        "faq": [
            {"q": "How many words did Ernest Hemingway write a day?", "a": "Hemingway averaged about 500 words a day. He tracked his daily output on a hand-drawn chart, and the figures ranged from around 450 on a normal day to over 1,000 on days when he worked ahead so he could take the next day off to go fishing."},
            {"q": "Why did Hemingway write so few words a day?", "a": "He deliberately kept the count low so he would never 'empty the well.' By stopping while he still knew what would happen next, he made sure the next morning started with momentum instead of a blank page. He also revised heavily as he wrote, so each word took more effort."},
            {"q": "Did Hemingway really track his word count?", "a": "Yes. According to George Plimpton's 1958 Paris Review interview, Hemingway kept a chart made from a cardboard packing box on which he recorded each day's word count, in his words, 'so as not to kid myself.'"},
        ],
        "profile_blurb": BLURB,
        "related_cards": [
            {"href": f"/writers-routines/{A}/standing-desk/", "kicker": "Hemingway", "title": "Did Hemingway Write Standing Up?"},
            {"href": f"/writers-routines/{A}/writing-schedule/", "kicker": "Hemingway", "title": "What Time Did Hemingway Write?"},
        ],
    },
    {
        "author_slug": A, "author_name": AN, "subslug": "standing-desk",
        "date_iso": DATE_ISO, "date_disp": DATE_DISP, "read_time": 5,
        "crumb": "Standing Desk",
        "title": "Did Ernest Hemingway Write Standing Up? | His Standing Desk Setup",
        "meta_desc": "Yes, Hemingway wrote standing up for most of his career. Here's the exact setup he used in Cuba, why he stood, and what he wrote by hand versus typewriter.",
        "og_title": "Did Ernest Hemingway Write Standing Up?",
        "og_desc": "Hemingway wrote standing at a chest-high board for most of his career. Here's the real setup and why he did it.",
        "tw_desc": "Yes. Hemingway stood to write, at a chest-high reading board in a pair of oversized loafers. Here's the full setup.",
        "h1": "Did Ernest Hemingway Write Standing Up?",
        "intro": "Yes. For most of his working life Hemingway wrote on his feet, and the setup was more specific than the legend suggests.",
        "answer": "Yes. Hemingway wrote standing up, at a chest-high board, for most of his career.",
        "answer_sub": "In his Cuba home he worked at a reading board set on top of a bookshelf, standing in a pair of oversized loafers. He drafted in pencil and switched to a typewriter for passages that came fast, like dialogue.",
        "blocks": [
            {"h2": "The Setup at Finca Vigia"},
            {"p": "The clearest account comes from George Plimpton, who visited Hemingway's home outside Havana for the 1958 <em>Paris Review</em> interview. Hemingway worked in his bedroom, standing at a reading board propped chest-high on top of a bookcase. He stood in a pair of his oversized loafers on the worn skin of a lesser kudu, one of his hunting trophies, with the animal's mounted head on the wall above him."},
            {"p": "His tools were split by task. First drafts went down in pencil on onionskin paper, slowly and with constant small revisions. When the writing came fast and clean, usually dialogue, he turned to the typewriter, which also stood at chest height so he never had to sit. He counted his pencils the way he counted his words, as a rough gauge of a day's work."},
            {"h2": "Why He Stood"},
            {"p": "Part of it was physical. Hemingway carried injuries his whole adult life, starting with shrapnel wounds from the First World War and compounded by two plane crashes in Africa in 1954. Sitting for long stretches was uncomfortable. Standing was easier on his back."},
            {"p": "But he had stood to write from the beginning, long before the worst of the injuries, so habit and temperament mattered more than pain. Standing kept him alert and kept sessions short, which suited a man whose method was to quit early while the work was still going well. You don't settle in for a marathon when you're on your feet. You do the morning's pages and you stop."},
            {"quote": "Writing and travel broaden your ass if not your mind, and I like to write standing up.", "by": "Ernest Hemingway, quoted in his letters"},
            FULL_LINE,
            {"h2": "What You Can Steal"},
            {"ul": [
                "<strong>Standing keeps sessions honest.</strong> It's harder to drift, snack, or stall on your feet. The discomfort is mild and the focus is real.",
                "<strong>Match the tool to the task.</strong> Hemingway drafted slow work in pencil and fast work on the typewriter. Use the slowest input for the hardest passages.",
                "<strong>Your desk is a cue, not a requirement.</strong> A dedicated spot and posture tell your brain it's time to work. The specifics matter less than the consistency.",
            ]},
        ],
        "faq": [
            {"q": "Did Ernest Hemingway write standing up?", "a": "Yes. For most of his career Hemingway wrote standing at a chest-high reading board set on top of a bookcase, a habit documented in George Plimpton's 1958 Paris Review interview at Hemingway's home in Cuba."},
            {"q": "Why did Hemingway write standing up?", "a": "Partly because old injuries, including First World War shrapnel and two 1954 plane crashes, made sitting uncomfortable. But he had stood to write from early in his career, and standing kept his sessions short and alert, which fit his habit of stopping while the work was still going well."},
            {"q": "Did Hemingway write by hand or on a typewriter?", "a": "Both. He drafted slow, difficult passages in pencil on onionskin paper and switched to the typewriter for faster material such as dialogue. Both were set up at chest height so he could work standing."},
        ],
        "profile_blurb": BLURB,
        "related_cards": [
            {"href": f"/writers-routines/{A}/writing-schedule/", "kicker": "Hemingway", "title": "What Time Did Hemingway Write?"},
            {"href": f"/writers-routines/{A}/stop-mid-sentence/", "kicker": "Hemingway", "title": "How Did Hemingway Know When to Stop?"},
        ],
    },
    {
        "author_slug": A, "author_name": AN, "subslug": "writing-schedule",
        "date_iso": DATE_ISO, "date_disp": DATE_DISP, "read_time": 5,
        "crumb": "Writing Schedule",
        "title": "What Time Did Ernest Hemingway Write? | His Daily Schedule",
        "meta_desc": "Hemingway wrote every morning starting at first light, usually around 6 a.m., and stopped by midday. Here's his daily writing schedule and the logic behind the early start.",
        "og_title": "What Time Did Ernest Hemingway Write?",
        "og_desc": "Hemingway wrote every morning from first light to midday. Here's his daily schedule and why he started so early.",
        "tw_desc": "First light to midday, every morning. Here's Hemingway's daily writing schedule and the reason for the early start.",
        "h1": "What Time Did Ernest Hemingway Write?",
        "intro": "Hemingway was a morning writer, and an early one. He started at first light and was usually done before lunch, with the rest of the day left for everything that wasn't writing.",
        "answer": "Every morning, starting at first light (around 6 a.m.) and finishing by midday.",
        "answer_sub": "He wrote in the cool early hours when no one could disturb him, then stopped around noon. Afternoons and evenings were for fishing, reading, and living, which he saw as fuel for the next morning's work.",
        "blocks": [
            {"h2": "First Light, Every Day"},
            {"p": "Hemingway laid out his schedule plainly in the 1958 <em>Paris Review</em> interview. He wrote first thing, as soon as there was light to see by, usually around six in the morning. The early start wasn't about willpower or productivity culture. It was about conditions. The house was silent, the air was cool, and his mind was clear before the day had a chance to crowd in."},
            {"quote": "When I am working on a book or a story I write every morning as soon after first light as possible. There is no one to disturb you and it is cool or cold and you come to your work and warm as you write.", "by": "Ernest Hemingway, <em>Paris Review</em>, 1958"},
            {"p": "He worked through the morning at a steady pace, standing at his board, and typically finished by noon. A morning's work was around <a href='/writers-routines/" + A + "/word-count/'>500 words</a>, sometimes more. Then he stopped, deliberately, while he still knew what would happen next."},
            {"h2": "Why Mornings Worked for Him"},
            {"p": "The early hours gave Hemingway two things he prized: solitude and a fresh head. He believed the writing should happen before the world got loud and before fatigue set in. By starting at dawn, he spent his sharpest hours on the page and his dullest hours on everything else."},
            {"p": "Just as important was what he did after. Hemingway didn't write all day. He fished, he read, he saw people, and he let the afternoon refill the well. The morning schedule only works if you respect the off-hours as part of the method rather than time stolen from it."},
            FULL_LINE,
            {"h2": "What You Can Steal"},
            {"ul": [
                "<strong>Write before the day starts.</strong> The early hours buy you silence and a clear head, the two things drafting needs most. Even thirty minutes before everyone wakes up beats two distracted hours later.",
                "<strong>Protect a hard stop.</strong> Hemingway quit by noon. A finish line keeps the session focused and leaves the rest of your day intact.",
                "<strong>Treat rest as part of the work.</strong> The afternoon off wasn't a reward, it was how the next morning got its fuel.",
            ]},
        ],
        "faq": [
            {"q": "What time did Ernest Hemingway write?", "a": "Hemingway wrote every morning starting as soon after first light as possible, usually around 6 a.m., and typically finished by midday. He described this schedule in his 1958 Paris Review interview."},
            {"q": "Did Hemingway write in the morning or at night?", "a": "The morning. He believed the early hours offered silence and a fresh mind, and he wanted his sharpest time spent on the page. He left afternoons and evenings for fishing, reading, and rest."},
            {"q": "How long did Hemingway write each day?", "a": "Roughly from first light until noon, a span of about five to six hours, though his actual output was modest at around 500 words because he wrote slowly and stopped while the work was still going well."},
        ],
        "profile_blurb": BLURB,
        "related_cards": [
            {"href": f"/writers-routines/{A}/stop-mid-sentence/", "kicker": "Hemingway", "title": "How Did Hemingway Know When to Stop?"},
            {"href": f"/writers-routines/{A}/word-count/", "kicker": "Hemingway", "title": "How Many Words Did Hemingway Write a Day?"},
        ],
    },
    {
        "author_slug": A, "author_name": AN, "subslug": "stop-mid-sentence",
        "date_iso": DATE_ISO, "date_disp": DATE_DISP, "read_time": 5,
        "crumb": "When to Stop",
        "title": "How Did Hemingway Know When to Stop Writing? | Stop While It's Going Good",
        "meta_desc": "Hemingway always stopped writing while it was still going well and he knew what came next. Here's his rule against writer's block and how to use it yourself.",
        "og_title": "Hemingway's Rule: Always Stop While the Going Is Good",
        "og_desc": "Hemingway stopped each day while it was still going well and he knew what came next. It was his cure for writer's block.",
        "tw_desc": "Hemingway's anti-block rule: stop while it's still going well and you know what happens next. Here's how to use it.",
        "h1": "How Did Hemingway Know When to Stop Writing Each Day?",
        "intro": "Most writers stop when they run dry. Hemingway did the opposite, and he believed it was the single most useful habit he ever built.",
        "answer": "He stopped while it was still going well and he knew exactly what would happen next.",
        "answer_sub": "By quitting mid-flow instead of writing himself empty, Hemingway guaranteed a running start the next morning. He called it never emptying the well, and he treated it as his defense against getting stuck.",
        "blocks": [
            {"h2": "Stop While You're Going Good"},
            {"p": "The rule is simple and it runs against instinct. When the writing is flowing and you know what comes next, that is exactly when you stop. Not when you're exhausted, not when you've hit a wall, but at the moment you'd most like to keep going."},
            {"quote": "The best way is always to stop when you are going good and when you know what will happen next. If you do that every day when you are writing a novel you will never be stuck.", "by": "Ernest Hemingway, <em>Paris Review</em>, 1958"},
            {"p": "He described the same idea in <em>A Moveable Feast</em> as never emptying the well. There was always something left in the deep part of it, and overnight the well refilled from the springs that fed it. Drain it completely and you face a dry hole the next morning. Leave water in it and you start the day with the level already rising."},
            {"h2": "Why It Beats Writer's Block"},
            {"p": "Writer's block usually strikes at the start of a session, when you sit down facing a blank space and no clear next move. Hemingway's habit eliminates that moment. Because he stopped the day before while he still knew what would happen next, he never began a morning from nothing. The first sentence was already waiting. He just had to write it down."},
            {"p": "There's a discipline cost. You have to walk away from good momentum, which feels wasteful in the moment. But the trade is worth it. You give up a little extra output today to protect against the far more expensive problem of a stalled tomorrow."},
            {"p": "It pairs naturally with his small <a href='/writers-routines/" + A + "/word-count/'>daily word count</a>. Stopping early and keeping the number modest are two halves of the same idea: never spend everything you have."},
            FULL_LINE,
            {"h2": "What You Can Steal"},
            {"ul": [
                "<strong>Quit mid-flow on purpose.</strong> Stop when you know the next line, not when you're empty. Tomorrow's session starts with momentum instead of dread.",
                "<strong>Leave a note for tomorrow.</strong> Jot the next beat or sentence before you walk away, so the running start is waiting when you return.",
                "<strong>Never empty the well.</strong> Keep something in reserve every day. The point isn't maximum output now, it's never facing a dry start.",
            ]},
        ],
        "faq": [
            {"q": "How did Hemingway avoid writer's block?", "a": "He stopped each day while the writing was still going well and he knew what would happen next. Because he never began a session from a blank slate, the dreaded blank-page moment that causes most blocks simply didn't occur."},
            {"q": "What did Hemingway mean by 'never empty the well'?", "a": "In A Moveable Feast he compared his writing to a well. He always left something in the deep part of it rather than draining it dry, so it could refill overnight and he would start the next day with the level already rising."},
            {"q": "Should you stop writing mid-sentence?", "a": "Hemingway's principle was to stop while you still know what comes next, which for many writers means stopping mid-scene or even mid-sentence. The goal is to leave yourself an obvious, easy place to pick up the next day."},
        ],
        "profile_blurb": BLURB,
        "related_cards": [
            {"href": f"/writers-routines/{A}/word-count/", "kicker": "Hemingway", "title": "How Many Words Did Hemingway Write a Day?"},
            {"href": f"/writers-routines/{A}/standing-desk/", "kicker": "Hemingway", "title": "Did Hemingway Write Standing Up?"},
        ],
    },
]

if __name__ == "__main__":
    for p in PAGES:
        print("wrote", build(p))
