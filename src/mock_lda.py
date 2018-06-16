import json

from src.clean_text import clean_text

scifi = "When the away team prepares to beam down, they invariably assume the transporter formation: standing upright, " \
        "usually with arms slack aside, all facing the camera. When they beam down, they reappear in the same formation " \
        "and poses, as that's how the transporter works. However, they do this even when it makes little sense, such as " \
        "when beaming into uncertain, hostile environments (where they usually proceed to draw phasers and look around " \
        "in a defensive circle. Sometimes it gets more silly - on a few occasions, they prep their phasers, holster them, " \
        "beam down, and immediately draw phasers again.We know that the transporter works with any formation or pose; " \
        "people and objects have been beamed lying down, holding large objects, holding each other in emergencies. But " \
        "routine transportation always involves everyone standing facing the same direction. Why do they do this? Is it " \
        "somehow related to how the transporter works? Or is it purely for out-of-universe reasons]" \
        "In most TNG, VOY and even DS9 episodes, [Starfleet security][1] personnel appear to be slow, unprepared and " \
        "tactically unimaginative when facing threats, especially intruders and boarding parties. Examples:" \
        "* Rather than convening at the nearest transporter room (because they insist that site-to-site is risky) and " \
        "transporting strategically to corner the intruder, they *walk hurriedly* along corridors." \
        "* They rarely take defensive postures or have quick reflexes and are often shot while standing." \
        "* During physical struggles, they show almost no martial arts training (only exception is the chief of security)" \
        "* They brainlessly follow standard procedure and rarely use decoys or other indirect or deceptive strategies. " \
        "They fall for deceptions all the time." \
        "* They don't bother with amour (we have seen people taking cover behind things such as overturned tables, so " \
        "there are materials that can at least limit phaser damage without weighing a person down too much)." \
        "* They don't use phasers in wide dispersal mode in situations that it would be useful." \
        "* Tactical away teams are rarely camouflaged (exception: TNG: Chain of Command)" \
        "* Security teams operate without a dedicated controller guiding them remotely (instead, they haphazardly make " \
        "radio contact with the *bridge* chief of security)" \
        "* And many other examples..." \
        "Out of universe, we have seen that later personnel, such as the [MACO][2]s and the alternate universe security " \
        "personnel seem to do better. But seriously, after wars with the Klingons, the Borg, the Dominion and various " \
        "other antagonists, how can Starfleet security be this poor? Surely there must be a clear line between being " \
        "peaceful and being naive." \
        " [1]: http://en.memory-alpha.org/wiki/Starfleet_Security" \
        "[2]: http://en.memory-alpha.org/wiki/MACO_personnel"

food = "So I overcooked both brown rice and potatoes today, both boiling. the skin on the potatoes was intact. when " \
       "overcooked i.e. too soft, does that mean the fiber is significantly reduced in both foods? does the fiber leech" \
       " out into the water?" \
       "Neither of these foods has much fiber to begin with, about 2 and 3 % fiber by weight, according to the first " \
       "website I found with data. I don't think it was the fiber that was holding them together before they got cooked" \
       "No, fiber is a very hardy beast chemically. There is no fiber lost at all, no matter how much you overcook them" \
       " in a dish. You would have to throw them into a furnace and take out crisps of carbon no longer recognizable as" \
       " food to change the fiber." \
       "Concord grapes, which most grape jellies/jams/preserves in the US are made from, are derived from the (US-native) " \
       "fox grape (Vitis labrusca) rather than (Europe-native) wine grape (Vitis vinifera). Common table grapes (the " \
       "ones eaten as fresh fruit) such as Thompson seedless are also derived from Vitis vinifera wine grapes." \
       "Fox grapes have a foxy taste character, which is a result of the presence of the naturally occurring compound methyl " \
       "anthranilate. Methyl anthranilate is a rather simple compound, and is used in many situations as an artificial " \
       "grape flavor. In many cases grape flavored candies, drinks and medicines are flavored not with grape extracts," \
       " but with synthetically produced methyl anthranilate. As such, these artificially flavored foods taste " \
       "like Concord grapes (fox grapes), rather than table or wine grapes." \
       "While it would be possible to come up with artificial wine grape flavor, the flavor profile of wine and table" \
       " grapes is not dominated by a single compound, as fox grapes are. Therefore, any such artificial wine grape" \
       " flavor would be much more expensive than artificial Concord grape flavor (i.e. just methyl anthranilate). " \
       "As such, when companies reach for grape flavor, they tend to go for the more inexpensive Concord grape flavor." \
       "This also adds to the persistent expectation (at least in the US) as to what grape flavored means. " \
       "Even if you came out with a wine-grape-flavored Jolly Rancher, many in the US would think it wouldn't " \
       "taste right, as they expect grape flavored things to taste like Concord grapes." \
       "Most pancake recipes call for all purpopse flour. I assume boxed mixes do the same, or a " \
       "mix of all purpose and cake flour for a lighter texture." \
       "The difference between them is 'hard' and 'soft' flours. Hard flours (AP, Bread, semolina, etc.)" \
       " have more gluten/protein in them, which contributes a chewier texture. Soft flours such as " \
       "cake are a finer grind and give cakes a crumblier (word?) and lighter texture. If you used AP " \
       "for an angel food cake, it would be dense and chewy, rather than light and airy." \
       "AP is generally a mix of hard and soft flours, and can be used for many cakes, breads, and of course pancakes. " \
       "Since pancakes tend to have a chewier texture than many baked goods, they probably use an AP-type flour." \
       "Since pancakes are reletively cheap to make, experiment with it. Try bread, AP, cake, and " \
       "varioius combinations. There is a recipe in Mark Bittman's How to Cook Everything where you " \
       "separate the eggs, whip the whites into a foam, and fold it into the batter before cooking. " \
       "I imagine this would go well with cake flour."

topics_dict = {}
topics_dict['scifi'] = list(clean_text(scifi))
topics_dict["food"] = list(clean_text(food))

file_system_json_file = open("./topics_mock_lda.json", "w")
file_system_json_file.write(json.dumps(topics_dict))
file_system_json_file.close()

scifi_words = "phaser, laser, enterprise, kirk, holodeck, photon, star, picard, weasley, transporter, federation, planets, klingon, ferengi, borg"
food_words = "meat, lamb, pork, salad, cheese, raw, cake, potatoes, eggs, tomatoes, pizza, eggplant, onion, sandwich, trout"

topics_dict = {}
topics_dict['scifi'] = list(clean_text(scifi_words))
topics_dict["food"] = list(clean_text(food_words))

file_system_json_file = open("./topics_mock_lda_v2.json", "w")
file_system_json_file.write(json.dumps(topics_dict))
file_system_json_file.close()