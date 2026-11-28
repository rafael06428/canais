import json, os, sys
# ---------- visual helpers ----------
def P(role, x, y=620, s=1, **kw): d = {"k": "p", "role": role, "x": x, "y": y, "s": s}; d.update(kw); return d
def I(k, **kw): d = {"k": k}; d.update(kw); return d
def V(bg, items=(), **kw): d = {"bg": bg, "items": list(items)}; d.update(kw); return d
YOU = lambda x, y=630, s=1, **kw: P("you42", x, y, s, **kw)
RUTH = lambda x, y=630, s=1, **kw: P("date", x, y, s, **kw)
BUCK = lambda x, y=630, s=1, **kw: P("cowboy", x, y, s, **kw)
STAN = lambda x, y=630, s=.9, **kw: P("busboy", x, y, s, **kw)
BD = lambda h: ["NOV 28, 1942", h]

S = []
def ch(t, y): S.append(("CH", t, y))
def sc(text, v): S.append((text, v))

ch("", "Intro")
sc("Tonight, more than a thousand people will squeeze into a Boston nightclub licensed for about four hundred and sixty. And you are one of them.",
   V("street", [P("gent", 300, 640, .9, pose="walk", dx=120, dxDur=6), RUTH(560, 640, .95), YOU(700, 640, 1), P("sailor42", 980, 640, .9, face="happy", seed=3)], time="night", badge=["NOV 28, 1942", None], focus=640))
sc("Before you walk in, look at the front door. It's a revolving door. It spins. Remember it.",
   V("foyer", [I("revdoor", x=640, y=560, s=1.1, spin=1.4), I("text", text="REMEMBER THIS DOOR", fs=60, y=150, at="@remember")], focus=640))
sc("In a few hours, that door will help decide who lives, and who doesn't.",
   V("foyer", [I("revdoor", x=640, y=560, s=1.1, spin=.3)], fx=["dark"], smoke=.25, focus=640))
sc("In about fifteen minutes, four hundred and ninety-two people will be gone.",
   V("black", [I("count", to=492, at=.6, dur=2.4, fs=150, y=380)], focus=640))
sc("Hour by hour, you'll face the choices they faced. And by the end, you'll know whether you would have survived.",
   V("street", [YOU(560, 640, 1.1, face="look"), RUTH(760, 640, 1.05, face="happy")], time="night", cam="in", focus=640))

ch("2:00 PM  ·  FENWAY PARK", "2 PM: Fenway Park")
sc("It's Saturday, November twenty-eighth, 1942. America has been at war for less than a year.",
   V("stadium", [], time="day", cheer=1, badge=BD("2 PM"), focus=640))
sc("You're twenty-one, a Navy sailor home on leave for Thanksgiving weekend. Your girl, Ruth, has come into Boston to see you.",
   V("stadium", [YOU(520, 640, 1.1, face="happy"), RUTH(760, 640, 1.05, face="happy")], time="day", focus=640))
sc("This afternoon you're at Fenway Park, for the biggest college football game of the season. Boston College against Holy Cross.",
   V("stadium", [I("text", text="BC  vs  HOLY CROSS", fs=70, y=200, at=1.0)], time="day", cheer=1, focus=640))
sc("Boston College hasn't lost all year. It's ranked number one, and a big bowl game is all but promised.",
   V("stadium", [I("text", text="UNBEATEN", fs=100, y=330, at=.5), I("text", text="#1", fs=80, y=470, c="#fff", at="@number")], time="day", focus=640))
sc("Then the impossible happens. Little Holy Cross wins. Fifty-five to twelve.",
   V("stadium", [YOU(400, 640, 1.05, face="shock"), RUTH(880, 640, 1.0, face="shock"), I("text", text="55 – 12", fs=130, y=330, at="@fifty-five")], time="day", cheer=1, focus=640))
sc("Boston College had planned a victory party for tonight, at the city's most glamorous nightclub, the Cocoanut Grove. Now the party is cancelled.",
   V("plain", [I("paper", x=640, y=360, title="PARTY CANCELLED", sub="Boston College celebration called off", at=.4, fs=30)], color="#2f4a5a", focus=640))
sc("For the team, it's the worst day of the season. Later, people will say that defeat saved their lives.",
   V("stadium", [P("gent2", 420, 640, 1, face="sad"), P("soldier42", 820, 640, 1, face="sad", seed=5)], time="dusk", focus=640))
sc("But the club won't be empty. It's a holiday weekend, in wartime, and the city is full of servicemen with a little money to spend.",
   V("street", [P("sailor42", 260, 640, .9, pose="walk", dx=200, dxDur=7, face="happy"), P("soldier42", 560, 640, .9, face="happy"), P("woman42", 800, 640, .85, face="happy"), P("gent", 1050, 640, .9)], time="dusk", focus=640))

ch("7:00 PM  ·  PIEDMONT STREET", "7 PM: Piedmont Street")
sc("By seven o'clock, you and Ruth are standing on Piedmont Street, in the cold, under a pink neon sign.",
   V("street", [YOU(520, 640, 1.05, shiver=1), RUTH(740, 640, 1.0, face="happy")], time="night", badge=BD("7 PM"), bubble={"text": "THE GROVE!", "x": 760, "y": 300}, focus=640))
sc("The Cocoanut Grove opened in the 1920s. For a while it belonged to a gangster named Charles Solomon, until he was killed in 1933.",
   V("street", [P("gent", 640, 640, 1.05, face="stern", look={"coat": "#1f1f24", "hatc": "#1a1a1a"}), I("text", text="1933", fs=90, y=330, at="@1933")], time="night", fx=["sepia"], focus=640))
sc("Now it's run by his lawyer, Barney Welansky, a man with friends at City Hall.",
   V("office", [P("owner", 560, 640, 1.1, face="calm"), I("table", x=820, y=500, w=260)], bubble={"text": "BARNEY WELANSKY", "x": 560, "y": 150}, focus=600))
sc("He's said to have bragged that he didn't need to follow the building code.",
   V("office", [P("owner", 560, 640, 1.1, face="happy", pose="point")], bubble={"text": "CODES? NOT FOR ME.", "x": 600, "y": 160}, focus=600))
sc("And just days before tonight, the club passed a fire inspection, with a good rating.",
   V("plain", [I("paper", x=640, y=360, title="FIRE RATING: GOOD", sub="Inspection, November 1942", at=.4, fs=30)], color="#3a3a4a", focus=640))
sc("You step into the revolving door. It turns, and you're inside. For most of the people here, it's the only way out they know.",
   V("foyer", [I("revdoor", x=640, y=560, s=1.1, spin=1.6), YOU(380, 640, .95, pose="walk"), RUTH(900, 640, .9)], focus=640))
sc("It's warm and loud. A girl at the checkroom takes your coats, and you head into the main room.",
   V("foyer", [P("waitress", 190, 600, .85, face="happy"), YOU(560, 640, 1), RUTH(760, 640, .95, face="happy")], focus=500))

ch("9:00 PM  ·  THE TROPICS", "9 PM: The tropics")
sc("Walking in is like stepping into the tropics. Fake palm trees. Leather walls. A ceiling covered in billowing cloth.",
   V("club", [YOU(420, 650, .95, face="look"), RUTH(600, 650, .9, face="happy")], badge=BD("9 PM"), cam="out", focus=520))
sc("In summer, the roof even rolls back, so you can dance under the stars.",
   V("club", [P("woman42", 470, 650, .9, pose="cheer", face="happy"), P("sailor42", 640, 650, .95, face="happy", seed=2)], focus=560))
sc("A band is playing. Waiters weave between the tables with trays of drinks. For a few hours, nobody is thinking about the war.",
   V("club", [P("waiter", 300, 650, .9, pose="walk", dx=300, dxDur=6), P("woman42", 760, 650, .85, face="happy", pose="cheer"), P("sailor42", 900, 650, .9, face="happy", pose="cheer", seed=7)], focus=640))
sc("Tonight, every table is full. People are squeezed in at the bars, on the dance floor, in the doorways.",
   V("club", [P("gent", 230, 650, .85), P("woman42", 370, 650, .8, face="happy"), P("soldier42", 520, 650, .85), P("sailor42", 690, 650, .85, seed=4), P("gent2", 860, 650, .85), P("woman42", 1010, 650, .8, look={"dress": "#6a3a6a"})], focus=620))
sc("Nobody is counting. But investigators will later estimate more than a thousand people inside. The legal limit, by most accounts, was about four hundred and sixty.",
   V("plain", [I("count", to=1000, pre="", post="+", at=.4, dur=2, fs=120, y=300), I("text", text="LIMIT: ABOUT 460", fs=60, y=470, c="#fff", at="@sixty")], color="#1f4a4f", focus=640))
sc("There are other doors, but you'd never know it. None of them has an exit sign.",
   V("club", [I("door", x=980, y=600, s=.9, label="EXIT?", labelY=-300)], cam="zoom", zoomAt=.5, cx=980, cy=420, focus=980))
sc("A door onto Shawmut Street is locked. Another has a bolt that keeps it shut. Some doors are hidden, and only the staff know where they are.",
   V("club", [I("door", x=420, y=600, s=.9, locked=True, label="SHAWMUT ST"), I("door", x=840, y=600, s=.9, locked=True)], focus=620))
sc("One old exit has even been replaced by a brick wall.",
   V("club", [I("door", x=640, y=600, s=1, brick=True)], bubble={"text": "A WALL?!", "x": 640, "y": 200, "tail": "center"}, focus=640))
sc("People will say the owner kept doors locked so nobody could slip out without paying. That was never proven.",
   V("office", [P("owner", 640, 640, 1.1, face="stern"), I("text", text="NEVER PROVEN", fs=64, y=230, at="@never")], focus=640))
sc("Across the room, you spot a famous face. Buck Jones, the cowboy movie star, is in town on a tour selling war bonds.",
   V("club", [BUCK(820, 650, 1.05, face="happy"), YOU(380, 650, .95, face="shock", pose="point")], bubble={"text": "BUCK JONES!", "x": 820, "y": 210}, focus=800))
sc("He's been feeling sick all day. But friends talked him into coming out for dinner.",
   V("club", [BUCK(620, 650, 1.05, face="sad"), P("gent", 860, 650, .95, face="happy", pose="point"), I("table", x=620, y=520, w=320)], focus=640))
sc("Ruth tugs your sleeve. Downstairs there's a cozy bar with a piano, the Melody Lounge. Do you go down, or stay up here, near the front door?",
   V("club", [RUTH(560, 650, 1.05, face="happy", pose="point"), YOU(760, 650, 1.05, face="look")], bubble={"text": "LET'S GO DOWN!", "x": 520, "y": 230}, focus=640))
sc("You go down. So do a lot of young couples tonight.",
   V("lounge", [YOU(300, 640, .95, pose="walk", dx=200, dxDur=5), RUTH(140, 640, .9, pose="walk", dx=200, dxDur=5)], focus=420))

ch("10:00 PM  ·  THE MELODY LOUNGE", "10 PM: The Melody Lounge")
sc("The stairs are narrow, only about four feet wide. They're the only public way in or out of this room.",
   V("lounge", [I("text", text="ONE WAY OUT", fs=72, y=250, at=1.2)], badge=BD("10 PM"), cam="zoom", zoomAt=.3, cx=160, cy=400, focus=260))
sc("It's dark down here, on purpose. The ceiling is draped in blue satin, with tiny lights like stars.",
   V("lounge", [I("piano", x=420, y=600, s=.9), P("woman42", 640, 640, .85, face="happy"), P("sailor42", 790, 640, .9, face="happy")], cam="out", focus=600))
sc("A pianist is playing, and people are singing along. It's the kind of place where you lose track of time.",
   V("lounge", [I("piano", x=520, y=600, s=1), P("gent2", 560, 600, .8, pose="sit", face="happy"), YOU(820, 640, .95, face="happy"), RUTH(980, 640, .9, face="happy")], focus=700))
sc("In the corner stands an artificial palm tree, with a light bulb hidden among its leaves.",
   V("lounge", [I("palm", x=720, y=600, s=1.1), I("bulb", x=720, y=320, s=.8)], cam="zoom", zoomAt=1.5, cx=720, cy=320, focus=720))
sc("A young soldier at the table next to it reaches up and unscrews that bulb. He wants a little darkness, to kiss his date.",
   V("lounge", [I("palm", x=760, y=600, s=1.1), I("bulb", x=760, y=320, s=.8, offAt="@unscrews"), P("soldier42", 600, 640, .95, pose="armsup", face="happy"), P("woman42", 430, 640, .9, face="happy")], focus=640))
sc("The bartender notices, and sends a busboy over to put it back.",
   V("lounge", [P("bartender", 1000, 640, 1, pose="point", face="stern"), STAN(640, 640)], bubble={"text": "FIX THAT LIGHT!", "x": 940, "y": 230, "tail": "right"}, focus=820))
sc("The busboy is Stanley Tomaszewski. He's sixteen, a high-school kid working long shifts for a couple of dollars and tips.",
   V("lounge", [STAN(640, 640, 1.05, face="calm"), I("text", text="AGE 16", fs=80, y=250, at="@sixteen")], focus=640))
sc("In the dark, he can't find the socket. So he lights a match.",
   V("lounge", [I("palm", x=760, y=600, s=1.1), STAN(620, 640, .95, pose="armsup", face="look"), I("match", x=680, y=360, s=1, at="@lights")], fx=["night"], focus=700))
sc("He finds it, screws the bulb back in, and blows out the match. At least, that's what he'll swear later.",
   V("lounge", [I("palm", x=760, y=600, s=1.1), I("bulb", x=760, y=320, s=.8, onAt="@screws"), STAN(620, 640, .95, face="calm")], focus=700))
sc("It's about ten fifteen. Upstairs, the big floor show is running late.",
   V("club", [P("waiter", 520, 650, .95, pose="walk", dx=150, dxDur=5), I("text", text="10:15 PM", fs=110, y=300, at=.4)], badge=BD("10:15 PM"), focus=640))

ch("10:15 PM  ·  THE PALM TREE", "10:15 PM: The palm tree")
sc("A moment later, someone points at the palm tree. There's a flicker in the leaves.",
   V("lounge", [I("palm", x=760, y=600, s=1.1, smokeAt=.8), P("woman42", 470, 640, .9, pose="point", face="shock")], focus=650))
sc("Then the fronds burst into flames.",
   V("lounge", [I("palm", x=700, y=600, s=1.15, fireAt=.4, fireDur=1.2), YOU(400, 640, .95, face="shock"), RUTH(1000, 640, .9, face="shock")], fx=["embers"], shakeAt=.4, focus=700))
sc("Bartenders throw water and seltzer at it. For a few seconds, it looks like they might put it out.",
   V("lounge", [I("palm", x=640, y=600, s=1.1, burning=True), P("bartender", 920, 640, .95, pose="point", face="worry")], bubble={"text": "WATER! QUICK!", "x": 920, "y": 230, "tail": "right"}, focus=760))
sc("A sailor who was there will remember it started slowly. Then, suddenly, it raced across the ceiling.",
   V("lounge", [I("palm", x=1100, y=600, s=1, burning=True), I("flames", x0=1100, x1=0, y=110, at="@raced", dur=1.6), P("sailor42", 520, 640, .95, face="shock")], fx=["embers", "glow"], focus=640))
sc("Burning cloth falls. Thick smoke fills the room. Then the lights go out.",
   V("lounge", [I("flames", x0=0, x1=1280, y=110, at=0, dur=.1), YOU(520, 640, 1, face="shock", pose="cover"), RUTH(720, 640, .95, face="shock")], fx=["embers", "dark"], smoke=.45, smokeAt=0, smokeDur=3, focus=620))
sc("Now you face the hardest choice of your life. Everyone around you is pushing toward the narrow stairs, the way they came in.",
   V("lounge", [P("gent", 300, 640, .85, pose="run", flip=True), P("woman42", 460, 640, .8, pose="run", flip=True), P("soldier42", 620, 640, .85, pose="run", flip=True), YOU(880, 640, 1, face="worry")], fx=["dark", "glow"], smoke=.4, focus=640))
sc("But a waiter behind the bar is waving people toward a door into the dark service corridors. Do you follow the crowd, or the waiter?",
   V("lounge", [P("waiter", 1040, 640, 1, pose="wave", face="worry"), YOU(700, 640, 1, face="worry"), RUTH(540, 640, .95, face="shock")], fx=["glow"], smoke=.4, bubble={"text": "THIS WAY!", "x": 1000, "y": 290, "tail": "right"}, focus=860))
sc("The crowd heads for the only exit it knows. The staff know other ways out.",
   V("kitchen", [P("waiter", 520, 640, .95, pose="run", face="worry"), YOU(760, 640, .95, pose="run", face="worry"), RUTH(940, 640, .9, pose="run", face="shock")], fx=["night"], smoke=.25, focus=700))

ch("MINUTES LATER  ·  THE DOOR", "Minutes later: The revolving door")
sc("Upstairs, the fire bursts out of the stairway and into the entrance hall.",
   V("foyer", [I("flames", x0=0, x1=1280, y=90, at=.2, dur=1.4), I("revdoor", x=820, y=560, s=1, spin=2)], fx=["embers", "glow"], smoke=.3, focus=640))
sc("Within minutes, it has spread through the whole club, fed by the cloth ceiling, the palm trees and the furniture.",
   V("club", [I("flames", x0=0, x1=1280, y=120, at=0, dur=2.5), I("palm", x=200, y=590, s=.9, fireAt=1.5), I("palm", x=1080, y=590, s=.9, fireAt=2.2)], fx=["embers", "glow"], smoke=.35, smokeAt=0, smokeDur=4, focus=640))
sc("Hundreds of people rush for the one door they know. The revolving door.",
   V("foyer", [I("revdoor", x=640, y=560, s=1.1, spin=3), P("gent", 300, 640, .85, pose="run"), P("woman42", 1000, 640, .8, pose="run", flip=True)], fx=["glow"], smoke=.3, focus=640))
sc("A few get out. Then so many people push from both sides that it jams.",
   V("foyer", [I("revdoor", x=640, y=560, s=1.1, spin=3, jamAt="@jams")], fx=["glow"], smoke=.35, shakeAt="@jams", focus=640))
sc("A door built to let people in a few at a time has become a wall.",
   V("foyer", [I("revdoor", x=640, y=560, s=1.1, spin=0, jamAt=0, jamMark=False), I("text", text="JAMMED", fs=110, y=380, c="#ff5a3a", at=.4)], fx=["glow"], smoke=.25, focus=640))
sc("Nearby, a brand-new lounge has its own exit. But that door opens inward, and the crowd pushes it shut with its own weight.",
   V("club", [I("door", x=640, y=600, s=1, label="OPENS INWARD", labelY=-300), P("gent2", 420, 640, .85, pose="armsup", face="shock"), P("soldier42", 860, 640, .85, pose="armsup", face="shock", flip=True)], fx=["glow"], smoke=.3, focus=640))
sc("In the dining room, a few people smash windows. Others are pulled to safety by waiters who know the hidden doors.",
   V("club", [P("waiter", 900, 650, .95, pose="wave", face="worry"), P("woman42", 640, 650, .85, pose="run"), I("door", x=1080, y=600, s=.85, open=True, openAt=.5)], fx=["glow"], smoke=.3, focus=860))
sc("One officer will later say that when the lights went out, everyone's good sense seemed to go out with them.",
   V("black", [I("text", text="THE LIGHTS WENT OUT", fs=64, y=360, c="#fff", at=.3)], focus=640))
sc("But nobody here was foolish. In the dark and the smoke, nobody could see a way out.",
   V("foyer", [YOU(640, 640, 1, face="sad")], fx=["dark"], smoke=.5, focus=640))

ch("THE COWBOY", "The cowboy star")
sc("At his table upstairs, Buck Jones is one of the most famous men in the room.",
   V("club", [BUCK(640, 650, 1.15, face="calm"), I("table", x=640, y=520, w=340)], fx=["sepia"], cam="in", focus=640))
sc("He has starred in more than a hundred westerns. On screen, he always finds a way out.",
   V("fields", [BUCK(640, 640, 1.1, face="happy", pose="point")], time="dusk", fx=["sepia"], bubble={"text": "THIS WAY, PARTNER!", "x": 660, "y": 170}, focus=640))
sc("Tonight there's no script. He's carried out alive, and rushed to Massachusetts General Hospital.",
   V("street", [P("fireman", 520, 640, 1, pose="hold", face="worry"), P("sailor42", 780, 640, .95, face="worry")], time="night", fire=True, smoke=.2, focus=640))
sc("Two days later, he dies. The news shocks the whole country.",
   V("plain", [I("paper", x=640, y=360, title="BUCK JONES DIES", sub="Film star a victim of Boston fire", at=.4, fs=30)], color="#2a2a30", focus=640))

ch("10:23 PM  ·  THE ALARMS", "10:23 PM: The alarms")
sc("Outside, by strange luck, fire engines are already close by. A few streets away, they were putting out a burning car.",
   V("street", [I("car", x=360, y=640, s=.9, c="#2a3a4a"), I("car", x=900, y=640, s=.8, truck=True, flip=True)], time="night", badge=BD("10:23 PM"), focus=640))
sc("A firefighter sees smoke pouring out of the Grove. More alarms go out, one after another.",
   V("street", [P("fireman", 560, 640, 1.05, pose="point", face="shock"), I("text", text="5 ALARMS", fs=100, y=320, at="@alarms")], time="night", fire=True, smoke=.25, focus=600))
sc("Sailors, soldiers and Coast Guardsmen in the street rush in to help. They form lines, and break through walls and doors.",
   V("street", [P("sailor42", 380, 640, .95, pose="run"), P("soldier42", 620, 640, .95, pose="armsup", face="stern"), P("sailor42", 860, 640, .95, pose="run", seed=6)], time="night", fire=True, smoke=.2, focus=620))
sc("The Navy sends trucks and medical teams from its shipyard across the harbor.",
   V("street", [I("car", x=640, y=640, s=1, c="#3a4a3a", dx=-200, dxDur=5)], time="night", fire=True, focus=640))
sc("A crowd gathers in the cold. Some are searching for friends and family who went inside and haven't come out.",
   V("street", [P("woman42", 460, 640, .95, face="worry", pose="pray"), P("gent", 720, 640, .95, face="worry"), P("soldier42", 940, 640, .9, face="sad")], time="night", fire=True, smoke=.15, focus=640))
sc("Firefighters fight their way inside. What they find near the doors, they will never forget.",
   V("foyer", [P("fireman", 640, 640, 1.1, face="sad", pose="hold")], fx=["dark"], smoke=.4, focus=640))
sc("But down in the kitchen, they find people still alive. Some of them hid inside a walk-in refrigerator, where the smoke couldn't reach them.",
   V("kitchen", [P("fireman", 600, 640, 1, pose="point", face="shock"), P("waitress", 980, 640, .85, face="worry"), P("gent2", 1100, 640, .85, face="worry")], fridgeOpen=True, smoke=.2, focus=900))
sc("From the first flicker in that palm tree, the worst was over in about fifteen minutes.",
   V("black", [I("text", text="15 MINUTES", fs=120, y=380, at=.5)], focus=640))

ch("MIDNIGHT  ·  THE HOSPITALS", "Midnight: The hospitals")
sc("At Boston City Hospital, the victims arrive about one every eleven seconds. Three hundred in a single hour.",
   V("hospital", [P("doctor", 420, 640, 1, face="worry", pose="point"), P("nurse", 680, 640, .95, pose="walk", dx=200, dxDur=4), I("count", to=300, at=1.5, dur=2, fs=110, y=230)], time="night", badge=BD("MIDNIGHT"), focus=560))
sc("Across town, Massachusetts General takes in more than a hundred people in about two hours.",
   V("hospital", [I("bed", x=420, y=600, s=.8), I("bed", x=900, y=600, s=.8), P("nurse", 660, 640, .9, face="worry")], time="night", focus=640))
sc("Doctors, nurses and volunteers work through the night. One hospital had practiced a disaster drill just the week before.",
   V("hospital", [P("nurse", 420, 640, .95, pose="walk", dx=150, dxDur=5), P("doctor", 760, 640, 1, face="stern", pose="point")], time="night", focus=600))
sc("Many are hurt less by the flames than by the smoke they breathed.",
   V("hospital", [P("doctor", 640, 640, 1.05, face="sad")], time="night", bubble={"text": "IT WAS THE SMOKE.", "x": 640, "y": 170}, focus=640))
sc("Doctors there try a gentler way to treat burns, with soft dressings instead of harsh dyes. It works, and it changes burn care for good.",
   V("hospital", [P("doctor", 560, 640, 1.05, face="calm", pose="hold"), I("bed", x=880, y=600, s=.8)], time="night", focus=640))
sc("Some patients also get a new drug almost no civilian has ever received. Penicillin.",
   V("hospital", [P("nurse", 620, 640, 1, face="calm"), I("text", text="PENICILLIN", fs=90, y=230, at="@penicillin")], time="night", focus=640))
sc("And a psychiatrist named Erich Lindemann talks with survivors and grieving families. His work becomes one of the first scientific studies of grief.",
   V("office", [P("doctor", 520, 640, 1, face="calm", look={"coat": "#3a3a42"}), P("woman42", 800, 640, .9, face="sad")], focus=640))

ch("AFTERMATH  ·  WHO WAS TO BLAME?", "Aftermath: Who was to blame?")
sc("So what started the fire? Almost at once, the newspapers blamed the busboy.",
   V("plain", [I("paper", x=640, y=360, title="BUSBOY'S MATCH?", sub="Boston, November 1942", at=.4, fs=30)], color="#3a3a4a", badge=["AFTERMATH", "1942-1946"], focus=640))
sc("But the fire commissioner's official report couldn't prove it. It called the cause unknown.",
   V("office", [P("gent", 520, 640, 1, face="stern"), I("paper", x=840, y=360, s=.8, title="CAUSE: UNKNOWN", sub="Official report", at=1.2, fs=28)], focus=640))
sc("Historians still argue about it. Some think leaking refrigerator gas, or faulty wiring, helped the fire spread so fast.",
   V("office", [I("text", text="UNKNOWN", fs=110, y=330, at=.4), I("text", text="WIRING?  GAS?", fs=60, y=470, c="#fff", at=2.0)], focus=640))
sc("Stanley Tomaszewski was cleared. But he carried the blame for the rest of his life. He died in 1994.",
   V("street", [STAN(640, 640, 1.05, face="sad")], time="dawn", fx=["sepia"], focus=640))
sc("Barney Welansky was convicted of manslaughter, and sentenced to twelve to fifteen years in prison.",
   V("office", [P("owner", 640, 640, 1.05, face="sad"), I("text", text="12 – 15 YEARS", fs=90, y=230, at="@sentenced")], focus=640))
sc("He served less than four. He was released, very ill, in 1946, and died only weeks later.",
   V("office", [P("owner", 640, 640, 1.0, face="sad", pose="sit")], fx=["sepia"], focus=640))
sc("The fire changed the law. Exits must be marked and lit. Exit doors must swing outward. Decorations can't be easily flammable.",
   V("club", [I("door", x=640, y=600, s=1, label="EXIT", labelY=-300, open=True, openAt=1.2)], focus=640))
sc("And a revolving door now needs ordinary swinging doors right beside it.",
   V("foyer", [I("revdoor", x=640, y=560, s=1, spin=1), I("door", x=330, y=560, s=1), I("door", x=950, y=560, s=1)], focus=640))

sc("The club itself was torn down years ago. Today, a small plaque in the sidewalk marks the place where it stood.",
   V("street", [P("modern", 640, 640, 1, face="sad")], time="day", fx=["sepia"], badge=["TODAY", None], focus=640))
ch("THE ANSWER  ·  WOULD YOU HAVE SURVIVED?", "Would you have survived?")
sc("So, would you have survived? Of the more than a thousand people inside, four hundred and ninety-two died.",
   V("black", [I("count", to=492, at=.3, dur=2, fs=140, y=330), I("text", text="OF 1,000+", fs=60, y=470, c="#fff", at=2.2)], badge=["NOV 28, 1942", None], focus=640))
sc("Many survivors did one of three things. They moved at the very first smoke. They found a window. Or they followed someone who knew another way out.",
   V("club", [I("text", text="MOVE EARLY", fs=56, y=200, at=1.6), I("text", text="FIND A WINDOW", fs=56, y=330, at="@window"), I("text", text="FOLLOW THE STAFF", fs=56, y=460, at="@followed")], focus=640))
sc("The waiters and kitchen workers knew the back corridors. Many of the people who followed them lived.",
   V("kitchen", [P("waiter", 560, 640, 1, pose="wave", face="calm"), YOU(840, 640, .95, face="calm")], focus=700))
sc("The people who waited, to finish a drink, to find a coat, to look for a friend, had far less time than they thought.",
   V("lounge", [I("palm", x=900, y=600, s=1, burning=True), YOU(500, 640, 1, face="worry")], fx=["glow"], smoke=.3, focus=640))
sc("If you followed that waiter into the dark, you probably made it out. If you went with the crowd to the stairs and the spinning door, your chances were far worse.",
   V("street", [YOU(560, 640, 1.05, face="sad"), RUTH(760, 640, 1.0, face="sad", pose="pray")], time="dawn", focus=640))
sc("Remember that revolving door? Next time you walk through one, look beside it. Those ordinary doors are there because of the Cocoanut Grove.",
   V("foyer", [I("revdoor", x=640, y=560, s=1, spin=.8), I("door", x=330, y=560, s=1), I("door", x=950, y=560, s=1), I("text", text="BECAUSE OF 1942", fs=60, y=120, at="@ordinary")], focus=640))
sc("Which choice would you have made? The crowd, or the waiter? Tell me in the comments.",
   V("lounge", [YOU(540, 640, 1.05, face="look"), P("waiter", 900, 640, 1, pose="wave")], bubble={"text": "THE CROWD?", "x": 300, "y": 220}, bubble2={"text": "THE WAITER?", "x": 900, "y": 300, "at": 2.0, "tail": "right"}, focus=700))

# ---------- assemble ----------
chapters = []; n = 0
for e in S:
    if e[0] == "CH": chapters.append({"title": e[1], "yt_chapter": e[2], "scenes": []}); continue
    t, v = e; chapters[-1]["scenes"].append({"text": t, "v": v}); n += 1
ALL = [s for c in chapters for s in c["scenes"]]
def find(sub): return next(i for i, s in enumerate(ALL) if sub in s["text"])
def B(text, key=None, fx=None, v=None, offset=None):
    d = {"text": text, "prompt": None}
    if offset is not None: d["offset"] = offset
    if key: d["src"] = find(key)
    if v is not None: d["v"] = v
    if fx is not None: d["fx"] = fx
    return d

FOOT = "Follow for a new story every day"
TAIL = "\n\nAnimated story based on historical accounts."
shorts = [
 # 0 cut: POV choice
 {"label": "ONE SPINNING DOOR", "footer": "Full story: Cocoanut Grove, 1942", "title": "1,000 People and One Spinning Door. Where Do You Run? #Shorts",
  "description": "Boston, 1942: a nightclub licensed for about 460 people, more than 1,000 inside, and a fire. Full story: {LONG_URL}" + TAIL + "\n\n#History #POV #CocoanutGrove #Shorts",
  "blocks": [B("do you run?", "Before you walk in"),
             B("Boston, 1942. You're in a nightclub licensed for about four hundred and sixty people. More than a thousand are inside.", "Nobody is counting"),
             B("A fire starts in a fake palm tree, and races across the cloth ceiling. The lights go out.", "A sailor who was there"),
             B("Everyone runs for the one door they know. A revolving door.", "Hundreds of people rush"),
             B("It jams. But a waiter is waving people toward the kitchen and the back corridors.", "But a waiter behind the bar", fx=900),
             B("Many who followed the staff lived. Four hundred and ninety-two people didn't. So, in the dark, where", "The crowd heads for")]},
 # 1 standalone: the animal formula
 {"label": "THE LAST PIGEON", "title": "The Pigeon That Saved 194 Soldiers #Shorts", "footer": FOOT, "standalone": True, "rate": "+12%",
  "description": "October 1918: trapped soldiers were being shelled by their own guns, and one wounded pigeon carried the message. Newest full story: {LONG_URL}" + TAIL + "\n\n#History #WW1 #CherAmi #Shorts",
  "blocks": [B("For heaven's sake, stop it.", v=V("plain", [I("paper", x=640, y=360, title="STOP IT.", sub="Argonne, October 4, 1918", at=0, fs=60, rot=-4)], color="#4a4a38", badge=["OCT 4, 1918", None], focus=640)),
             B("October 1918, the Argonne Forest. More than five hundred American soldiers are trapped, surrounded by German troops.",
               v=V("forest", [P("doughboy", 520, 640, 1, face="worry"), P("doughboy", 760, 640, .95, face="worry", seed=3)], time="grey", focus=640)),
             B("Then their own artillery starts shelling them, by mistake.",
               v=V("forest", [P("doughboy", 640, 640, 1, face="shock", pose="cover")], time="grey", fx=["shake", "embers"], smoke=.2, focus=640)),
             B("Their commander, Major Charles Whittlesey, reportedly has one homing pigeon left. Its name is Cher Ami.",
               v=V("forest", [P("major", 560, 640, 1.05, face="stern"), I("pigeon", x=700, y=430, s=.9, note=True)], time="grey", bubble={"text": "CHER AMI", "x": 700, "y": 300}, focus=640)),
             B("Shot in the chest, blinded in one eye, its leg nearly torn off, it keeps flying. About twenty-five miles.",
               v=V("fields", [I("pigeon", x=160, y=330, s=1.1, fly=True, hurt=True, dx=300, dy=-40, dur=6)], time="grey", fx=["wind"], focus=360)),
             B("The shelling stops, and about a hundred and ninety-four men walk out alive. Historians still argue over some details.",
               v=V("forest", [P("doughboy", 420, 640, 1, pose="cheer", face="happy"), P("major", 640, 640, 1, face="calm"), P("doughboy", 860, 640, 1, pose="cheer", face="happy", seed=4)], time="dawn", focus=640)),
             B("The real message said: Our own artillery is dropping a barrage directly on us.",
               v=V("plain", [I("paper", x=640, y=360, title="STOP IT.", sub="Argonne, October 4, 1918", at=0, fs=60, rot=-4)], color="#4a4a38", focus=640))]},
 # 2 cut: POV choice
 {"label": "THE PALM TREE", "footer": "Full story: Cocoanut Grove, 1942", "title": "The Palm Tree Is Smoking. Do You Leave Your Drink? #Shorts",
  "description": "November 1942, the Melody Lounge in Boston: a fake palm tree starts to smoke. What do you do? Full story: {LONG_URL}" + TAIL + "\n\n#History #POV #CocoanutGrove #Shorts",
  "blocks": [B("or finish your drink?", "Then the fronds burst", offset=2.0),
             B("Boston, November 1942. You're in the Melody Lounge, a dark basement bar under a famous nightclub.", "It's dark down here"),
             B("In the corner, a fake palm tree starts to smoke.", "A moment later, someone points"),
             B("Bartenders throw water on it. It looks like they've got it.", "Bartenders throw water"),
             B("Then the fire races across the cloth ceiling. The lights go out. There's one narrow staircase.", "Burning cloth falls"),
             B("In minutes, the whole club is burning. The people who moved first had the best chance. So, do you run for the stairs right now,", "Within minutes, it has spread")]},
 # 3 standalone: the "found in..." formula
 {"label": "FOUND UNDER THE ICE", "title": "Found 3,000 Meters Under the Ice: Shackleton's Lost Ship #Shorts", "footer": FOOT, "standalone": True,
  "description": "In 2022, explorers found Shackleton's Endurance 106 years after the Antarctic ice crushed it. Newest full story: {LONG_URL}" + TAIL + "\n\n#History #Shackleton #Endurance #Shorts",
  "blocks": [B("still standing upright on the seabed.", v=V("underwater", [I("wreck", x=640, y=600, s=1, name="ENDURANCE", lightAt=0)], badge=["MARCH 2022", None], focus=640)),
             B("November 1915. Ernest Shackleton's ship Endurance is crushed by the Antarctic ice.",
               v=V("ice", [{"k": "ship", "x": 640, "y": 470, "s": .8, "tilt": 14, "tiltDur": 4, "broken": 2}], time="grey", badge=["NOV 21, 1915", None], focus=640)),
             B("All twenty-eight men watch it sink. Every one of them will make it home alive.",
               v=V("ice", [P("polar", 560, 640, .8, face="sad"), P("polar", 700, 640, .8, face="sad", seed=2), {"k": "ship", "x": 980, "y": 470, "s": .5, "sink": .9, "sinkDur": 5}], time="grey", focus=640)),
             B("For more than a century, nobody can find it. The ice is too thick, and the sea is too deep.",
               v=V("ice", [I("text", text="LOST", fs=120, y=300, at=.5)], time="grey", fx=["snow"], focus=640)),
             B("Then, in March 2022, an underwater robot dives about three thousand meters.",
               v=V("underwater", [I("raw", svg='<g transform="translate(640,200)"><rect x="-70" y="-30" width="140" height="60" rx="14" fill="#e0b021" stroke="#1a1a1a" stroke-width="4"/><circle cx="70" cy="0" r="40" fill="url(#lamp)"/></g>'), I("count", to=3000, post=" m", at=.8, dur=2.5, fs=90, y=430)], badge=["MARCH 2022", None], focus=640)),
             B("There it is. Its name still on the stern. Its wheel still in place.",
               v=V("underwater", [I("wreck", x=640, y=600, s=1.05, name="ENDURANCE", lightAt=.3)], cam="zoom", zoomAt=1.0, cx=640, cy=520, focus=700)),
             B("The freezing water had preserved it almost perfectly. After a hundred and six years, Shackleton's ship was",
               v=V("underwater", [P("scientist", 640, 640, 1, face="happy", pose="cheer")], focus=640))]},
 # 4 cut: strange object
 {"label": "WHY THIS DOOR?", "footer": "Full story: Cocoanut Grove, 1942", "title": "Why Every Revolving Door Has a Normal Door Next to It #Shorts",
  "description": "It goes back to one night in Boston, in 1942. Full story: {LONG_URL}" + TAIL + "\n\n#History #CocoanutGrove #FireSafety #Shorts",
  "blocks": [B("a normal door right next to it.", "And a revolving door now needs", fx=470),
             B("Look closely next time. In 1942, a Boston nightclub called the Cocoanut Grove had one main entrance: a revolving door.", "Before you walk in"),
             B("That night, a fire raced through the club in minutes.", "Within minutes, it has spread"),
             B("Hundreds of people pushed on that door at once, and it jammed.", "A few get out"),
             B("Another exit opened inward, and the crowd pushed it shut. Others were locked.", "Nearby, a brand-new lounge"),
             B("Four hundred and ninety-two people died. After that, the law changed. That's why a revolving door has", "The fire changed the law")]},
 # 5 cut: parallel person
 {"label": "HE WAS 16", "footer": "Full story: Cocoanut Grove, 1942", "title": "He Was 16 and Lit a Match to Fix a Light Bulb #Shorts",
  "description": "Stanley Tomaszewski was a 16-year-old busboy in Boston in 1942. He was blamed for a fire he may never have caused. Full story: {LONG_URL}" + TAIL + "\n\n#History #CocoanutGrove #Boston #Shorts",
  "blocks": [B("for the rest of his life.", "Stanley Tomaszewski was cleared"),
             B("Boston, November 1942. A busboy named Stanley Tomaszewski is sixteen years old.", "The busboy is Stanley"),
             B("A young soldier has unscrewed a light bulb in a fake palm tree, to kiss his date in the dark.", "A young soldier at the table"),
             B("Stanley is sent to fix it. He can't see the socket, so he lights a match.", "In the dark, he can't find"),
             B("Minutes later, the palm tree is on fire. Four hundred and ninety-two people die.", "Then the fronds burst"),
             B("Investigators never proved what started it, and Stanley was cleared. But he carried the blame", "But the fire commissioner")]},
]

EP = {
 "slug": "cocoanut-grove-1942",
 "title": "24 Hours in the Cocoanut Grove Fire, 1942",
 "title_yt": "24 Hours in the Cocoanut Grove Fire, 1942: Would You Have Survived?",
 "description": "November 28, 1942. You're a 21-year-old Navy sailor on Thanksgiving leave in Boston. Tonight, more than a thousand people will squeeze into the Cocoanut Grove, a nightclub licensed for about 460, and its main door is a revolving door. At about 10:15 p.m. a fake palm tree in the basement bar catches fire. Within minutes the whole club is burning. Hour by hour, what would you have done, and would you have survived?\n\n{CHAPTERS}\n\nSources: Boston Fire Historical Society, \"The Story of the Cocoanut Grove Fire\"; National Archives, Prologue Magazine (Fall 2017), \"The Cocoanut Grove Fire\"; Smithsonian Magazine, \"Three Medical Breakthroughs That Can Be Traced Back to a Tragic Nightclub Fire\"; History.com, \"The Tragic Story of America's Deadliest Nightclub Fire\"; EBSCO Research Starters; All That's Interesting; Massachusetts General Hospital history.\n\nSources disagree on some details: the legal capacity (most say about 460, one says 600), the injury count, and the exact charges against the owner. The official cause of the fire was never determined, and the busboy was cleared. The main character and his date are fictional; the places, events and named people are real. Animated story, with AI-assisted narration, based on historical accounts.\n\n#History #POV #CocoanutGrove",
 "tags": ["cocoanut grove fire", "cocoanut grove", "boston history", "nightclub fire", "1942", "fire safety history", "buck jones", "revolving door", "would you survive", "history", "pov history", "animated history", "ww2 home front", "boston", "true story"],
 "voice": "en-US-AndrewMultilingualNeural",
 "thumb_text": "ONE DOOR.\n1,000 PEOPLE.",
 "thumb_scene": find("Then the fronds burst"),
 "thumb_t": 2.2, "thumb_dx": 490,
 "title_card": {"after_scene": 5, "lines": ["24 HOURS IN THE COCOANUT GROVE FIRE", "WOULD YOU HAVE SURVIVED?"]},
 "style": "cartoon",
 "chapters": chapters, "shorts": shorts,
}
out = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/ep"
os.makedirs(out, exist_ok=True)
json.dump(EP, open(f"{out}/episode.json", "w"), indent=1, ensure_ascii=False)
words = sum(len(s["text"].split()) for s in ALL)
print("scenes", n, "words", words)
for s in shorts: print(s["label"], len(s["blocks"]), sum(len(b["text"].split()) for b in s["blocks"]), [b.get("src") for b in s["blocks"]])
