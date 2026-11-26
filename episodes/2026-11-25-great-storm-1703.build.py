import json
# ---------- visual helpers ----------
def P(role, x, y=600, s=1, **kw): d = {"k": "p", "role": role, "x": x, "y": y, "s": s}; d.update(kw); return d
def SHIP(x, y=470, s=1, **kw): d = {"k": "ship", "x": x, "y": y, "s": s}; d.update(kw); return d
def I(k, **kw): d = {"k": k}; d.update(kw); return d
def V(bg, items=(), **kw): d = {"bg": bg, "items": list(items)}; d.update(kw); return d
YOU = lambda x, y=620, s=1, **kw: P("you", x, y, s, **kw)
OLD = lambda x, y=620, s=1, **kw: P("sailor", x, y, s, seed=2.2, **kw)

S = []
def ch(t, y): S.append(("CH", t, y))
def sc(text, v): S.append((text, v))

ch("", "Intro")
sc("Twenty-four hours from now, the worst storm in British history will tear across England. And you are in exactly the wrong place.",
   V("sea", [SHIP(330, 470, .7), SHIP(700, 455, .55), SHIP(1020, 470, .65)], time="day", storm=0, badge=["NOV 26, 1703", None], focus=700))
sc("You're on a warship, anchored a few miles off the coast of Kent, next to a sandbank sailors have a nickname for. The Great Ship Swallower.",
   V("sands", [SHIP(1050, 450, .45), I("text", text="THE GREAT SHIP SWALLOWER", fs=64, y=250, at="@swallower")], time="day", storm=0, focus=640))
sc("Remember that name. Before this is over, it will swallow more than a thousand men.",
   V("sands", [I("raw", svg='<path d="M500 600 L520 520 L540 600" stroke="#4a3020" stroke-width="10" fill="none"/><path d="M800 610 L815 540" stroke="#4a3020" stroke-width="10"/>')], time="dusk", storm=1, focus=640))
sc("Thousands more will die on land and at sea, in a single night.",
   V("london", [I("roofs", y=430, n=5, fall=[None, 1.0, None, 1.6, None])], time="night", storm=3, fx=["wind", "rain", "lightning"], focus=560))
sc("Hour by hour, you'll face the choices they faced. And by the end, you'll know whether you would have survived.",
   V("deck", [YOU(560, 640, 1.1, face="look"), I("lantern", x=900, y=380, s=1.2)], time="dusk", storm=1, focus=560))

ch("8:00 AM  ·  THE DOWNS", "8 AM: The Downs")
sc("It's Friday, November twenty-sixth, 1703, by the calendar England used at the time. You're seventeen, a sailor on HMS Stirling Castle.",
   V("deck", [YOU(520, 640, 1.1), OLD(820, 640, 1.05, face="happy")], time="day", storm=1, badge=["NOV 26, 1703", "8 AM"], focus=600))
sc("She's a seventy-gun ship of the Royal Navy, with nearly three hundred men packed on board.",
   V("sea", [SHIP(640, 470, 1.05, sails="furled")], time="day", storm=1, cam="in", focus=640))
sc("Your fleet has just come home from a long campaign in the Mediterranean. Everyone is tired, and everyone wants to go ashore.",
   V("below", [P("sailor", 300, 640, 1, face="sleep"), YOU(640, 640, 1.05, face="sad"), P("sailor2", 960, 640, 1, face="worry", seed=4)], storm=1, focus=640))
sc("This stretch of water is called the Downs. It's usually a safe place to wait, sheltered by the coast of Kent.",
   V("beach", [SHIP(780, 400, .35), SHIP(1000, 395, .3), SHIP(1180, 405, .32), I("boat", x=420, y=560, s=.7)], time="day", storm=0, focus=900))
sc("The town of Deal sits right on the beach. You can see its rooftops from the deck.",
   V("beach", [P("townsman", 520, 620, .9, pose="walk", dx=160, dxDur=6), P("woman", 820, 620, .85, seed=1)], time="day", storm=0, focus=640))
sc("But a few miles behind you lie the Goodwin Sands. At low tide they look like an island. At high tide they vanish.",
   V("sands", [I("text", text="GOODWIN SANDS", fs=70, y=300, at=1.0)], time="day", storm=0, focus=640))
sc("Ships that touch them get stuck, and the sand pulls them down. That's how the bank earned its nickname.",
   V("sands", [SHIP(640, 520, .7, tilt=12, tiltDur=3, sink=.35, sinkDur=6, broken=2)], time="grey", storm=1, focus=640))
sc("The wind has been blowing hard for days. Nobody aboard thinks much of it. Winter gales are normal here.",
   V("deck", [OLD(460, 640, 1.05), YOU(760, 640, 1.05, face="calm")], time="day", storm=1, fx=["wind"], bubble={"text": "JUST A GALE.", "x": 520, "y": 160}, focus=600))
sc("The admiral, Sir Cloudesley Shovell, has already taken the biggest ships up the river to safety.",
   V("sea", [SHIP(500, 470, .7, sails="set", dx=420, dxDur=8), P("admiral", 1120, 640, .8)], time="day", storm=1, focus=700))
sc("The rest of the squadron, including yours, stays here, under Rear Admiral Basil Beaumont on a ship called the Mary.",
   V("sea", [SHIP(420, 470, .6), SHIP(840, 465, .7, lights=False), I("flag", x=1180, y=640, c="#b8322a")], time="day", storm=1, bubble={"text": "THE MARY", "x": 840, "y": 150}, focus=840))

ch("AFTERNOON  ·  THE FALLING GLASS", "Afternoon: The falling glass")
sc("By the afternoon, the sky has turned a strange copper colour, and the sea is a mess of white crests.",
   V("sea", [SHIP(640, 470, .8)], time="dusk", storm=2, fx=["wind"], badge=['NOV 26, 1703', 'AFTERNOON'], focus=640))
sc("On land, a clergyman named William Derham is watching his barometer. The needle keeps falling.",
   V("room", [P("bishop", 400, 620, 1, look={"coat": "#2a2a30"}, face="worry"), I("gauge", x=820, y=330, s=1, at=.5, dur=5, **{"from": .7, "to": .05})], time="dusk", fireplace=True, wall="#bfa680", focus=600))
sc("He'll later record the lowest air pressure he has ever seen. He's never seen a storm like the one that's coming.",
   V("room", [I("gauge", x=640, y=330, s=1.3, at=0, dur=1, **{"from": .05, "to": .02}), I("text", text="LOWEST EVER", fs=60, y=600, at=1.5)], time="dusk", wall="#bfa680", focus=640))
sc("Aboard the Stirling Castle, the officers order extra anchors dropped. Thick ropes groan against the waves.",
   V("deck", [P("officer", 420, 640, 1.05, pose="point"), YOU(820, 640, 1, face="worry", pose="cling")], time="dusk", storm=2, fx=["wind", "spray"], bubble={"text": "MORE ANCHORS!", "x": 470, "y": 150}, focus=560))
sc("You ask the old sailor in the next hammock if this is bad. He's been at sea for thirty years.",
   V("below", [YOU(460, 640, 1, face="worry"), OLD(800, 640, 1.05, face="stern"), I("lantern", x=640, y=160, s=1.3)], storm=2, bubble={"text": "IS THIS BAD?", "x": 420, "y": 160}, focus=640))
sc("He doesn't answer. He just ties his shoes tighter.",
   V("below", [OLD(640, 640, 1.2, face="stern", pose="kneel"), I("lantern", x=900, y=160, s=1.2)], storm=2, focus=640))
sc("Here's your first choice. Ships' boats still go to the beach for supplies. You could ask to go with one.",
   V("beach", [I("boat", x=640, y=470, s=.8, dx=-200, dxDur=8), SHIP(1120, 390, .3)], time="dusk", storm=2, fx=["wind"], bubble={"text": "GO ASHORE?", "x": 640, "y": 170, "tail": "center"}, focus=640))
sc("If you made it ashore tonight, your chances of seeing morning would be far, far better. But you're not allowed. You stay on board.",
   V("deck", [YOU(640, 640, 1.1, face="sad"), P("officer", 980, 640, 1, face="stern")], time="dusk", storm=2, fx=["wind"], bubble={"text": "NO LEAVE.", "x": 980, "y": 150, "tail": "right"}, focus=760))

ch("10:00 PM  ·  THE WIND", "10 PM: The wind")
sc("By ten at night, the wind isn't a sound anymore. It's a weight. It presses on the ship like a giant hand.",
   V("sea", [SHIP(640, 480, .9, lights=True)], time="night", storm=3, fx=["wind", "rain", "lightning"], badge=['NOV 26, 1703', '10 PM'], focus=640))
sc("Below deck, nobody sleeps. Hammocks swing so hard they slam into each other.",
   V("below", [P("sailor", 320, 640, 1, face="shock"), YOU(640, 640, 1.05, face="shock", shiver=1), P("sailor2", 960, 640, 1, face="worry", seed=3), I("lantern", x=640, y=150, s=1.2)], storm=3, fx=["shake"], focus=640))
sc("Men pray out loud. Some of them haven't prayed in years.",
   V("below", [P("sailor", 420, 640, 1.05, pose="pray", face="sad"), P("sailor2", 840, 640, 1.05, pose="pray", face="sleep", seed=5), I("lantern", x=640, y=150, s=1.2)], storm=3, focus=640))
sc("Some estimates suggest gusts of over a hundred miles an hour. Enough to rip roofs off and flatten whole forests.",
   V("fields", [I("tree", x=260, y=600, s=1), I("tree", x=560, y=590, s=.9, fallAt=1.5), I("tree", x=880, y=600, s=1.05), I("tree", x=1140, y=590, s=.9, fallAt=3)], time="night", storm=3, fx=["wind", "rain"], focus=640))
sc("And it's not just your ship. Across the whole south of England, people are lying awake, listening to their houses shake.",
   V("room", [I("bed", x=640, y=600, s=1), P("woman", 560, 520, .8, pose="sleep", face="worry")], time="night", fx=["lightning"], shakeAt=1, storm=2, focus=640))

ch("MEANWHILE  ·  LONDON", "Meanwhile: London")
sc("Seventy miles away, London is being torn apart.",
   V("london", [I("roofs", y=430, n=5, fall=[None, .8, None, None, 2.2])], time="night", storm=3, fx=["wind", "rain", "lightning"], badge=['NOV 26, 1703', 'NIGHT'], focus=640))
sc("Chimneys snap off rooftops and crash through the houses below. Around two thousand chimney stacks come down in a single night.",
   V("london", [I("roofs", y=420, n=4, fall=[.5, 1.2, 2.0, 2.8]), I("count", to=2000, at=1, dur=3, fs=110, y=250, post=" CHIMNEYS")], time="night", storm=3, fx=["wind", "rain"], focus=640))
sc("Roof tiles fly through the air like knives. Nobody dares to go out into the street.",
   V("london", [I("debris", n=14, y=120, h=420), P("townsman", 640, 640, 1, pose="cover", face="shock")], time="night", storm=3, fx=["wind", "rain"], focus=640))
sc("The wind peels the lead off the roof of Westminster Abbey and flings it away.",
   V("london", [I("raw", svg='<path d="M640 160 L560 300 L720 300 Z" fill="#7a7a86" stroke="#1a1a1a" stroke-width="4"/>'), I("debris", n=8, y=150, h=200), I("text", text="WESTMINSTER ABBEY", fs=54, y=560, c="#fff", at=.6)], time="night", storm=3, fx=["wind", "rain", "lightning"], focus=640))
sc("At St James's Palace, Queen Anne is taken down into a cellar for safety.",
   V("cellar", [P("queen", 640, 620, 1.15, face="worry"), P("maid", 360, 620, .95, pose="hold"), P("officer", 920, 620, 1, face="stern")], badge=["NOV 26, 1703", "MIDNIGHT"], focus=640))
sc("On the river Thames, around seven hundred ships are smashed together in a giant tangle of wood and rope.",
   V("river", [SHIP(260, 470, .45, tilt=-14, tiltDur=1), SHIP(520, 480, .5, tilt=18, tiltDur=1.5, broken=1), SHIP(800, 470, .45, tilt=-8, tiltDur=1), SHIP(1060, 480, .5, tilt=22, tiltDur=2, broken=2)], time="night", storm=3, fx=["wind", "rain"], focus=640))

ch("MIDNIGHT  ·  THE CABLES", "Midnight: The cables")
sc("Back in the Downs, it's around midnight when you hear it. A crack like a cannon shot from the front of the ship.",
   V("deck", [YOU(640, 640, 1.1, face="shock", pose="cling")], time="night", storm=3, fx=["wind", "rain", "lightning"], shakeAt=.6, focus=640))
sc("One of the anchor cables has snapped.",
   V("sea", [SHIP(820, 470, .7, lights=True), I("rope", x1=560, y1=500, x2=120, y2=700, snapAt=.4)], time="night", storm=3, fx=["wind", "rain"], focus=560))
sc("Then another. The ship is still held by the last ones, but it's straining, jerking, groaning like it's in pain.",
   V("sea", [SHIP(760, 470, .75, lights=True), I("rope", x1=520, y1=500, x2=80, y2=690, snapAt=.8), I("rope", x1=540, y1=520, x2=200, y2=720)], time="night", storm=3, fx=["wind", "rain", "lightning"], focus=560))
sc("The officers shout orders nobody can hear. The wind tears the words straight out of their mouths.",
   V("deck", [P("officer", 500, 640, 1.1, pose="point", face="shock"), YOU(880, 640, 1, face="worry", pose="cling")], time="night", storm=3, fx=["wind", "rain"], bubble={"text": "...!!", "x": 560, "y": 150}, focus=640))
sc("Now you face the hardest choice of the night. If the ship breaks loose, where do you want to be?",
   V("deck", [YOU(640, 640, 1.15, face="worry")], time="night", storm=3, fx=["wind", "rain"], bubble={"text": "BELOW DECK", "x": 360, "y": 200}, bubble2={"text": "UP THE MAST", "x": 920, "y": 200, "tail": "right"}, focus=640))
sc("Below deck, it's dry. But if the ship rolls over, below deck is a trap with no way out.",
   V("below", [YOU(640, 640, 1.05, face="shock"), I("lantern", x=640, y=150, s=1.2)], storm=3, fx=["shake"], focus=640))
sc("Up on deck, the waves will try to sweep you away. But if the ship stays upright, the masts and rigging are the last thing to go under.",
   V("deck", [YOU(640, 600, 1.05, face="stern", pose="cling"), OLD(900, 640, 1, pose="cling", face="stern")], time="night", storm=3, fx=["wind", "rain", "spray"], focus=760))
sc("The old sailor grabs your arm and pulls you up the ladder. Up. Always up.",
   V("deck", [OLD(520, 640, 1.05, pose="point", face="stern"), YOU(820, 640, 1, face="shock", pose="walk")], time="night", storm=3, fx=["wind", "rain"], bubble={"text": "UP! ALWAYS UP!", "x": 520, "y": 150}, focus=640))
sc("Sometime in the early hours, the last cable gives way. The Stirling Castle is loose, and the wind is pushing her straight toward the Goodwin Sands.",
   V("sea", [SHIP(400, 470, .75, lights=True, dx=500, dxDur=7, tilt=8, tiltDur=4), I("rope", x1=300, y1=500, x2=40, y2=700, snapAt=.3)], time="night", storm=3, fx=["wind", "rain", "lightning"], badge=["NOV 27, 1703", "1 AM"], focus=700))

ch("MEANWHILE  ·  THE LIGHTHOUSE", "Meanwhile: The lighthouse")
sc("Far to the west, off the coast of Plymouth, a man is living out his dream, and his nightmare.",
   V("sea", [I("lighthouse", x=640, y=560, s=1)], time="night", storm=3, fx=["wind", "rain", "lightning"], focus=640))
sc("Henry Winstanley is an engineer and inventor. Years ago, he lost two of his own ships on a deadly reef called the Eddystone rocks.",
   V("desk", [P("winstanley", 460, 640, 1.1, face="sad"), I("table", x=860, y=500, w=380), I("paper", x=860, y=360, s=.6, title="EDDYSTONE", sub="ROCKS", at=.8)], badge=['1690s', None], focus=640))
sc("So he did something nobody had done before. He built a lighthouse right on top of the rocks, in the open sea.",
   V("sea", [I("lighthouse", x=640, y=560, s=1.1), P("winstanley", 980, 640, .8, face="happy", pose="point")], time="day", storm=0, focus=640))
sc("He was so proud of it that he said he wanted to be inside it during the greatest storm there ever was.",
   V("sea", [I("lighthouse", x=520, y=560, s=1), P("winstanley", 940, 640, .9, face="happy", pose="cheer")], time="dusk", storm=1, bubble={"text": "THE GREATEST STORM!", "x": 880, "y": 140, "tail": "right"}, focus=760))
sc("Tonight, he's there, fixing the light. With him are five other people.",
   V("sea", [I("lighthouse", x=640, y=560, s=1.15)], time="night", storm=3, fx=["wind", "rain", "lightning", "spray"], cam="zoom", zoomAt=.5, cy=250, badge=['NOV 27, 1703', 'NIGHT'], focus=640))
sc("By morning, there will be almost nothing left of the lighthouse. Just a few iron bars sticking out of the rock. No trace of the six people inside will ever be found.",
   V("sea", [I("lighthouse", x=640, y=560, s=1.1, goneAt=1.5)], time="dawn", storm=2, fx=["wind"], focus=640))

ch("2:00 AM  ·  THE SANDS", "2 AM: The sands")
sc("Back on the Stirling Castle, you feel it before you understand it. A long, grinding shudder under your feet.",
   V("deck", [YOU(640, 600, 1.1, face="shock", pose="cling")], time="night", storm=3, fx=["wind", "rain", "shake"], badge=['NOV 27, 1703', '2 AM'], focus=640))
sc("The ship has hit the Goodwin Sands.",
   V("sands", [SHIP(640, 500, .8, tilt=16, tiltDur=1.5, lights=True)], time="night", storm=3, fx=["wind", "rain", "lightning"], shakeAt=.2, focus=640))
sc("She tilts. Waves that were beside you are now on top of you, crashing across the deck.",
   V("deck", [YOU(640, 600, 1.05, face="shock", pose="cling"), I("wave", dur=1.6, **{"from": .8})], time="night", storm=3, fx=["wind", "rain", "spray"], focus=640))
sc("You climb. Your fingers are numb, the rope is soaking wet, and every gust tries to peel you off it.",
   V("sea", [I("raw", svg='<rect x="620" y="-20" width="40" height="760" fill="#4a3020" stroke="#1a1a1a" stroke-width="4"/><path d="M500 0 L700 720 M780 0 L580 720" stroke="#3a2a1a" stroke-width="6"/>'), YOU(600, 470, 1, face="stern", pose="cling", shiver=1)], time="night", storm=3, fx=["wind", "rain", "lightning"], focus=620))
sc("Around you in the darkness, other ships are hitting the sands too.",
   V("sands", [SHIP(300, 510, .45, tilt=-20, tiltDur=2, broken=1), SHIP(700, 500, .5, tilt=14, tiltDur=2), SHIP(1080, 510, .45, tilt=24, tiltDur=2, broken=2)], time="night", storm=3, fx=["wind", "rain", "lightning"], focus=700))
sc("The Northumberland goes down with all of her crew, around two hundred and twenty men.",
   V("sands", [SHIP(640, 510, .7, tilt=30, tiltDur=2, broken=2, sink=1, sinkAt=1.5, sinkDur=4), I("count", to=220, at=1, dur=2, fs=100, y=230, post=" LOST")], time="night", storm=3, fx=["wind", "rain"], focus=640))
sc("The Restoration is lost with everyone aboard, nearly four hundred men.",
   V("sands", [SHIP(640, 510, .7, tilt=-26, tiltDur=2, broken=3, sink=1, sinkAt=1.2, sinkDur=4), I("count", to=387, at=1, dur=2, fs=100, y=230, post=" LOST")], time="night", storm=3, fx=["wind", "rain", "lightning"], focus=640))
sc("And the Mary, the admiral's ship, breaks apart. Rear Admiral Beaumont dies with more than two hundred and sixty of his men.",
   V("sands", [SHIP(640, 510, .7, tilt=20, tiltDur=1.5, broken=3, sink=1, sinkAt=2, sinkDur=4), P("admiral", 1080, 640, .7, face="sad")], time="night", storm=3, fx=["wind", "rain"], focus=640))
sc("From the whole crew of the Mary, records name just one survivor: a sailor called Thomas Atkins.",
   V("sea", [P("sailor2", 640, 640, 1, face="worry", pose="cling", seed=7), I("text", text="1 SURVIVOR", fs=90, y=200, at=1.2)], time="night", storm=3, fx=["wind", "rain"], focus=640))
sc("You can't see any of this. You can only hear it. Screams, then cracking timber, then nothing but the wind.",
   V("black", [I("raw", svg='<path d="M0 360 Q160 300 320 360 T640 360 T960 360 T1280 360" stroke="#3a4a5a" stroke-width="6" fill="none"/>')], color="#06090f", focus=640))

ch("MEANWHILE  ·  INLAND", "Meanwhile: Inland")
sc("Inland, the storm is just as merciless.",
   V("fields", [I("tree", x=300, y=600, s=1), I("tree", x=1000, y=600, s=1.05, fallAt=1.2), I("windmill", x=660, y=600, s=1)], time="night", storm=3, fx=["wind", "rain"], focus=660))
sc("Windmills spin so fast that some of them catch fire from the friction. Hundreds of them are destroyed.",
   V("fields", [I("windmill", x=640, y=620, s=1.3, speed=9, fireAt=1)], time="night", storm=3, fx=["wind"], focus=640))
sc("In the New Forest alone, around four thousand oak trees are torn out of the ground.",
   V("fields", [I("tree", x=180, y=600, s=.8, fallAt=.6), I("tree", x=420, y=600, s=.9, fallAt=1.1), I("tree", x=660, y=600, s=.85, fallAt=1.6), I("tree", x=900, y=600, s=.9, fallAt=2.1), I("tree", x=1140, y=600, s=.8, fallAt=2.6), I("count", to=4000, at=1, dur=2.5, fs=100, y=200, post=" OAKS")], time="night", storm=3, fx=["wind", "rain"], focus=660))
sc("In the city of Wells, the Bishop, Richard Kidder, is asleep in bed with his wife when a chimney stack falls through the roof.",
   V("room", [I("bed", x=640, y=600, s=1.1, blanket="#6a4a7a"), P("bishop", 520, 512, .7, pose="sleep", face="sleep"), P("wife", 600, 512, .7, pose="sleep", face="sleep")], time="night", storm=2, fx=["lightning"], shakeAt=4, focus=640))
sc("Both of them are killed. In the West Country, the sea floods the land, and hundreds drown on the Somerset Levels.",
   V("fields", [I("tree", x=300, y=600, s=.9), I("raw", svg='<path d="M800 520 L840 470 L880 520 Z" fill="#b08a62" stroke="#1a1a1a" stroke-width="4"/>')], time="dawn", storm=2, flood=1, fx=["rain"], focus=640))

ch("DAWN  ·  DEAL BEACH", "Dawn: Deal beach")
sc("Morning comes, grey and wild. On the beach at Deal, people stare out to sea in horror.",
   V("beach", [P("townsman", 380, 640, 1, face="shock"), P("woman", 600, 640, .9, face="sad", seed=3), P("boatman", 840, 640, 1, face="worry")], time="grey", storm=2, fx=["wind"], badge=["NOV 27, 1703", "DAWN"], focus=600))
sc("Out on the Goodwin Sands, they can see the wrecks. And on them, tiny figures, waving for help.",
   V("sands", [SHIP(500, 540, .5, tilt=24, broken=2), SHIP(900, 545, .45, tilt=-18, broken=3), YOU(540, 478, .28, pose="wave", face="worry")], time="grey", storm=2, fx=["wind"], focus=600))
sc("One of those figures is you. You've been clinging to the rigging for hours. You can't feel your hands anymore.",
   V("sea", [I("raw", svg='<rect x="620" y="-20" width="40" height="760" fill="#4a3020" stroke="#1a1a1a" stroke-width="4"/><path d="M500 0 L700 720 M780 0 L580 720" stroke="#3a2a1a" stroke-width="6"/>'), YOU(600, 480, 1.05, face="sad", pose="cling", shiver=1)], time="grey", storm=2, fx=["wind", "spray"], focus=620))
sc("But the sea is still so violent that boats can't even be launched from the beach.",
   V("beach", [I("boat", x=600, y=560, s=.8), P("boatman", 380, 640, 1, face="stern"), P("boatman", 840, 640, 1, face="worry", seed=5, look={"capc": "#7a3a2a"})], time="grey", storm=3, fx=["wind", "spray"], focus=600))
sc("And not everyone in Deal is in a hurry to help. Daniel Defoe later accused some boatmen of grabbing what floated ashore instead of saving lives.",
   V("beach", [P("boatman", 520, 640, 1, face="happy", pose="hold"), I("raw", svg='<rect x="760" y="560" width="90" height="60" fill="#8a5a34" stroke="#1a1a1a" stroke-width="4"/>'), P("defoe", 1040, 640, .9, face="stern", pose="point")], time="grey", storm=1, focus=760))
sc("But one man, a shopkeeper named Thomas Powell, offers his own money: five shillings for every sailor brought back alive.",
   V("beach", [P("townsman", 560, 640, 1.1, pose="armsup", face="stern", look={"coat": "#3a5a3a"}), I("text", text="5 SHILLINGS", fs=80, y=190, at=1.5, sub="FOR EVERY SAILOR SAVED")], time="grey", storm=2, fx=["wind"], focus=600))
sc("Defoe credits him with saving around two hundred lives.",
   V("beach", [I("boat", x=640, y=470, s=.9, dx=-250, dxDur=6), P("townsman", 1000, 640, 1, face="happy", look={"coat": "#3a5a3a"})], time="grey", storm=2, fx=["wind"], focus=640))
sc("For the men on the Stirling Castle, the night doesn't end at dawn. You hang on through the whole day, and into another night.",
   V("sands", [SHIP(640, 540, .6, tilt=26, broken=2)], time="night", storm=2, fx=["wind", "rain"], badge=["NOV 27, 1703", "NIGHT"], focus=640))
sc("By the next morning, the other wrecks around you have disappeared. Only the Stirling Castle is still above the water.",
   V("sands", [SHIP(640, 560, .6, tilt=30, broken=3)], time="dawn", storm=1, badge=["NOV 28, 1703", "MORNING"], focus=640))
sc("Finally, the boats reach you. Seventy men are pulled off the Stirling Castle alive. More than two hundred are not.",
   V("sea", [I("boat", x=640, y=560, s=1.1), YOU(560, 600, .6, face="sad"), P("boatman", 720, 600, .6, pose="row"), I("count", to=70, at=1.5, dur=1.5, fs=100, y=200, post=" SAVED", c="#7fe07f")], time="dawn", storm=1, focus=640))

ch("AFTERMATH", "Aftermath")
sc("When the wind finally dies down, Britain counts its dead.",
   V("church", [P("woman", 400, 640, 1, pose="pray", face="sad"), P("townsman", 640, 640, 1, pose="pray", face="sad", seed=2), P("maid", 880, 640, .95, pose="pray", face="sleep")], badge=['DEC 1703', None], focus=640))
sc("Most estimates say at least eight thousand people died, many of them sailors. Some historians think the true number was even higher.",
   V("black", [I("count", to=8000, at=.4, dur=2.5, fs=140, y=360, pre="", post="+", c="#ffd21f")], focus=640))
sc("The Royal Navy loses more than a dozen ships, and well over a thousand men. On the Goodwin Sands alone, more than a thousand sailors are gone.",
   V("sands", [I("raw", svg='<path d="M420 600 L440 470 M700 610 L712 500 M930 620 L950 520" stroke="#4a3020" stroke-width="10"/>'), I("text", text="1,000+ SAILORS", fs=80, y=230, at=1.5)], time="grey", storm=0, focus=640))
sc("Queen Anne calls it a calamity and orders a national day of fasting and prayer.",
   V("church", [P("queen", 640, 640, 1.15, pose="pray", face="sad")], focus=640))
sc("Many preachers say the storm was God's punishment for the sins of the nation.",
   V("church", [P("bishop", 640, 640, 1.15, pose="point", face="stern")], bubble={"text": "PUNISHMENT!", "x": 700, "y": 140}, focus=640))

ch("HOW WE KNOW", "How we know")
sc("So how do we know all this, more than three hundred years later? Partly because of one writer.",
   V("desk", [P("defoe", 640, 640, 1.15, face="look")], badge=['1704', None], focus=640))
sc("Daniel Defoe, who would later write Robinson Crusoe, places newspaper ads asking ordinary people to send him their stories of the storm.",
   V("desk", [P("defoe", 420, 640, 1.05, pose="write"), I("table", x=640, y=500, w=520), I("candle", x=760, y=500, s=1), I("paper", x=950, y=320, s=.7, title="WANTED:", sub="YOUR STORY OF THE STORM", at=1.5, fs=40)], focus=640))
sc("Letters pour in from all over the country. He picks around sixty of them and publishes a whole book, called The Storm.",
   V("desk", [I("paper", x=420, y=360, s=.6, rot=-8, title="LETTER", at=0), I("paper", x=640, y=340, s=.6, rot=4, title="LETTER", at=.5), I("paper", x=860, y=370, s=.6, rot=-3, title="LETTER", at=1), I("paper", x=640, y=360, s=1, rot=0, title="THE STORM", sub="DANIEL DEFOE, 1704", at=2.6, fs=46)], focus=640))
sc("Some people call it one of the first books ever built from readers' own reports. A kind of social media, three centuries early.",
   V("plain", [I("paper", x=640, y=360, s=1.05, rot=-2, title="THE STORM", sub="DANIEL DEFOE, 1704", at=0, fs=46)], color="#e9dcc0", focus=640))
sc("And then there's the sea itself. The Goodwin Sands are always moving. Sometimes they bury things. Sometimes they give them back.",
   V("sands", [], time="day", storm=0, cam="out", focus=640))
sc("In 1979, divers exploring the sands found the wreck of the Stirling Castle, uncovered by the shifting sand.",
   V("underwater", [P("diver", 420, 560, .9, pose="point", face="look"), I("raw", svg='<path d="M700 620 Q820 520 1040 560 L1080 640 L700 650Z" fill="#5a3a22" stroke="#1a1a1a" stroke-width="5"/><path d="M760 600 L760 420 M900 590 L920 450" stroke="#4a3020" stroke-width="12"/>')], badge=["1979", None], focus=600))
sc("Her cannons were still there. So were the sailors' belongings, the everyday things of men like you.",
   V("underwater", [I("cannon", x=600, y=610, s=1, rot=-6), I("cannon", x=900, y=620, s=.9, rot=8), P("diver", 340, 520, .8, pose="hold", face="happy")], focus=640))

ch("THE ANSWER", "Would you have survived?")
sc("So, would you have survived the Great Storm of 1703?",
   V("deck", [YOU(640, 640, 1.15, face="look")], time="dawn", storm=0, badge=["NOV 26, 1703", None], focus=640))
sc("If you'd been on the Mary, almost certainly not. One man in more than two hundred and sixty came back.",
   V("sands", [SHIP(640, 560, .6, tilt=30, broken=3, sink=.5)], time="grey", storm=1, bubble={"text": "1 SURVIVOR", "x": 640, "y": 160, "tail": "center"}, focus=640))
sc("On the Stirling Castle, your odds were about one in four. And they depended on the choice you made at midnight. Up, not down.",
   V("sea", [I("raw", svg='<rect x="620" y="-20" width="40" height="760" fill="#4a3020" stroke="#1a1a1a" stroke-width="4"/>'), YOU(600, 480, 1, face="stern", pose="cling")], time="dawn", storm=1, bubble={"text": "UP. ALWAYS UP.", "x": 900, "y": 160, "tail": "left"}, focus=640))
sc("If you'd gone ashore that afternoon, you'd probably have lived, as long as you stayed away from falling chimneys.",
   V("london", [I("roofs", y=430, n=5, fall=[None, None, 1.2, None, None]), YOU(640, 660, .9, face="worry", pose="cover")], time="day", storm=1, focus=640))
sc("Remember the Great Ship Swallower? It took the Stirling Castle in one night. It took almost three hundred years to give her back.",
   V("sands", [I("text", text="THE GREAT SHIP SWALLOWER", fs=60, y=250, at=.3)], time="dusk", storm=0, focus=640))
sc("Would you have climbed the mast, or stayed below? Tell me in the comments.",
   V("deck", [YOU(520, 640, 1.1, face="happy", pose="wave"), OLD(860, 640, 1.05, face="happy")], time="dawn", storm=0, bubble={"text": "MAST OR BELOW?", "x": 640, "y": 150, "tail": "center"}, focus=640))

# ---------- assemble ----------
chapters = []; n = 0
for e in S:
    if e[0] == "CH": chapters.append({"title": e[1], "yt_chapter": e[2], "scenes": []}); continue
    t, v = e; chapters[-1]["scenes"].append({"text": t, "v": v}); n += 1
ALL = [s for c in chapters for s in c["scenes"]]
def find(sub): return next(i for i, s in enumerate(ALL) if sub in s["text"])
def B(text, key=None, fx=None):
    d = {"text": text, "prompt": None}
    if key: d["src"] = find(key)
    if fx is not None: d["fx"] = fx
    return d

shorts = [
 {"label": "THE SHIP SWALLOWER", "title": "The Sandbank That Swallowed 1,000 Sailors in One Night #Shorts",
  "description": "In November 1703, the worst storm in British history drove a Royal Navy squadron onto the Goodwin Sands. Full story: {LONG_URL}\n\nAnimated story based on historical accounts.\n\n#History #GreatStorm #Shipwreck #Shorts",
  "blocks": [B("in a single night.", "Thousands more will die"),
             B("Off the coast of Kent lies a sandbank sailors call the Great Ship Swallower.", "Remember that name"),
             B("At low tide it looks like an island. At high tide, it vanishes.", "At low tide"),
             B("In November 1703, the worst storm in British history drove a whole squadron of warships onto it.", "Sometime in the early hours"),
             B("The Northumberland. The Restoration. The admiral's ship, the Mary.", "The Restoration is lost"),
             B("More than a thousand sailors swallowed by the sand", "Out on the Goodwin Sands, they can see")]},
 {"label": "HE WISHED FOR THIS", "title": "He Wished to Be in His Lighthouse During the Greatest Storm Ever #Shorts",
  "description": "Henry Winstanley built the first lighthouse on the Eddystone rocks, and said he wanted to be inside it during the greatest storm there ever was. Full story: {LONG_URL}\n\nAnimated story based on historical accounts.\n\n#History #Lighthouse #GreatStorm #Shorts",
  "blocks": [B("there ever was.", "He was so proud"),
             B("Henry Winstanley lost two of his own ships on a deadly reef in the open sea.", "Henry Winstanley is an engineer", fx=560),
             B("So he built a lighthouse right on top of it. The first of its kind.", "So he did something"),
             B("He was so proud, he said he wanted to be inside it during the greatest storm there ever was.", "He was so proud"),
             B("In November 1703, he got his wish. He was there, fixing the light, when the storm hit.", "Tonight, he's there"),
             B("By morning, the lighthouse was gone. And so was he. He'd wished for the greatest storm", "By morning, there will be almost")]},
 {"label": "UP, NOT DOWN", "title": "Your Warship Is Breaking Loose. Do You Go Up or Down? #Shorts",
  "description": "November 1703: your anchor cables are snapping in the worst storm in British history. Where do you go? Full story: {LONG_URL}\n\nAnimated story based on historical accounts.\n\n#History #POV #Shipwreck #Shorts",
  "blocks": [B("the mast or below deck?", "Now you face the hardest choice"),
             B("It's midnight, November 1703. You're seventeen, on a warship off the coast of Kent.", "It's Friday, November"),
             B("The worst storm in British history is ripping your anchor cables apart.", "Then another. The ship"),
             B("Below deck is dry, but if the ship rolls over, it's a trap.", "Below deck, it's dry"),
             B("Up in the rigging, the wind tries to tear you off. But the masts are the last thing to go under.", "You climb. Your fingers"),
             B("Seventy men survived, clinging on for more than a day. So where would you go,", "Finally, the boats reach you")]},
 {"label": "5 SHILLINGS A LIFE", "title": "He Paid 5 Shillings for Every Sailor Saved #Shorts",
  "description": "After the Great Storm of 1703, a shopkeeper in Deal paid boatmen out of his own pocket to rescue shipwrecked sailors. Full story: {LONG_URL}\n\nAnimated story based on historical accounts.\n\n#History #GreatStorm #Heroes #Shorts",
  "blocks": [B("five shillings a life.", "But one man, a shopkeeper"),
             B("November 1703. After the worst storm in British history, sailors are stranded on wrecks off the town of Deal.", "Out on the Goodwin Sands, they can see"),
             B("They wave for help. But not everyone on the beach is in a hurry to save them.", "And not everyone in Deal"),
             B("So a local shopkeeper, Thomas Powell, pays boatmen out of his own pocket.", "Defoe credits him"),
             B("Daniel Defoe later credited him with around two hundred lives. All for", "Finally, the boats reach you")]},
]

EP = {
 "slug": "great-storm-1703",
 "title": "24 Hours in the Great Storm of 1703",
 "title_yt": "24 Hours in the Great Storm of 1703: Would You Have Survived?",
 "description": "November 26, 1703. You're a 17-year-old sailor on HMS Stirling Castle, anchored off the coast of Kent, a few miles from a sandbank sailors call the Great Ship Swallower. That night, the worst storm in British history tears across England: chimneys fall in London, the Queen hides in a cellar, a lighthouse vanishes with its builder inside, and a whole squadron of warships is driven onto the Goodwin Sands. Hour by hour, what would you have done, and would you have survived?\n\n{CHAPTERS}\n\nSources: Daniel Defoe, The Storm (1704); Royal Museums Greenwich, \"The Great Storm of 1703\"; Goodwin Sands Conservation Trust, \"Deal and the Great Storm of 1703\"; Wikipedia, \"Great storm of 1703\", \"Henry Winstanley\", \"Richard Kidder\"; History Today; University of York Borthwick Institute.\n\nDates use the Julian calendar England used in 1703 (November 26 = December 7 in today's calendar). Death tolls and wind speeds are estimates and sources disagree; the narration follows the most common figures. The main character and his shipmate are fictional; the ships, places and named people are real. Animation and narration are AI-assisted, based on historical accounts.\n\n#History #POV #GreatStorm",
 "tags": ["great storm 1703", "great storm of 1703", "goodwin sands", "stirling castle", "royal navy history", "daniel defoe", "eddystone lighthouse", "henry winstanley", "would you survive", "history", "pov history", "animated history", "shipwreck", "british history", "queen anne"],
 "voice": "en-US-AndrewMultilingualNeural",
 "thumb_text": "1,000 SAILORS\nIN ONE NIGHT",
 "thumb_scene": find("The ship has hit the Goodwin Sands"),
 "thumb_t": 2.5, "thumb_dx": 260,
 "title_card": {"after_scene": 5, "lines": ["24 HOURS IN THE GREAT STORM OF 1703", "WOULD YOU HAVE SURVIVED?"]},
 "style": "cartoon",
 "chapters": chapters, "shorts": shorts,
}
json.dump(EP, open("/home/claude/ep2/episode.json", "w"), indent=1, ensure_ascii=False)
words = sum(len(s["text"].split()) for s in ALL)
print("scenes", n, "words", words)
for s in shorts: print(s["label"], len(s["blocks"]), sum(len(b["text"].split()) for b in s["blocks"]), [b.get("src") for b in s["blocks"]])
