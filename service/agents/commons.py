from dataclasses import dataclass, field

joy_table = {
    10: 'Extremely Joyful: The response is full of exuberance, celebration, and uncontainable happiness. The person is overjoyed, possibly expressing their excitement through enthusiastic words, exclamations, or even laughter.',
    9: 'Very Joyful: The response is filled with happiness and delight. The person is very cheerful and clearly pleased with the situation, often showing their joy through positive expressions and a buoyant tone.',
    8: 'Joyful: The response conveys clear happiness and contentment. The person is in a good mood, expressing their joy openly, though not overwhelmingly so.',
    7: 'Quite Joyful: The response indicates a strong sense of happiness, though it may be slightly more reserved. The person is pleased and satisfied, with a clear sense of joy in their tone.',
    6: 'Moderately Joyful: The response shows a good level of happiness, with the person feeling positive and upbeat. The joy is present but might be tempered by other factors or emotions.',
    5: 'Slightly Joyful: The response indicates mild happiness. The person is in a positive mood, but their joy is more subdued and not the dominant emotion.',
    4: 'Barely Joyful: The response contains only a hint of joy. The person might be pleased or content, but the emotion is very understated and not strongly expressed.',
    3: 'Minimal Joy: The response shows just a small amount of happiness, perhaps a faint smile or a brief moment of positivity. The joy is present but very faint.',
    2: 'Very Little Joy: The response indicates only a trace of happiness. The person might acknowledge something positive but with little enthusiasm or expression of joy.',
    1: 'Almost No Joy: The response shows negligible joy. The person might be neutral or indifferent, with very little evidence of happiness or positive emotion.',
    0: 'No Joy: The response is completely devoid of joy. The person may feel neutral or even negative, with no expression of happiness, satisfaction, or positive emotion.',
}

anger_table = {
    10: 'Extremely Angry: The response is filled with intense, uncontrollable anger. The person may use harsh language, shout, or express their fury in a very aggressive and hostile manner. This is the peak of anger, possibly leading to destructive behavior.',
    9: 'Very Angry: The response conveys strong anger, with the person visibly upset and using forceful language. They might be confrontational, expressing their anger through pointed criticism or raised voice.',
    8: 'Angry: The response shows clear anger, with the person expressing their frustration or displeasure openly. The tone is sharp, and the person may be quite confrontational, though not at the highest intensity.',
    7: 'Quite Angry: The response indicates a strong sense of irritation or anger. The person is clearly upset and may be curt or sarcastic, showing their anger in a controlled but noticeable way.',
    6: 'Moderately Angry: The response shows a moderate level of anger. The person is clearly annoyed or frustrated, but their anger is somewhat restrained. They might express their displeasure firmly but without extreme hostility.',
    5: 'Slightly Angry: The response indicates mild anger. The person is irritated or displeased, but the emotion is not overwhelming. They might express their anger in a passive-aggressive or slightly sharp manner.',
    4: 'Barely Angry: The response contains a slight hint of anger. The person may be annoyed or somewhat displeased, but the emotion is minimal and might only show through subtle cues.',
    3: 'Minimal Anger: The response shows just a trace of anger. The person might express slight irritation or frustration, but the emotion is barely noticeable.',
    2: 'Very Little Anger: The response indicates only a very small amount of anger. The person might feel mildly irritated, but the emotion is almost negligible.',
    1: 'Almost No Anger: The response shows barely any anger. The person is mostly calm, with only the slightest hint of annoyance or frustration.',
    0: 'No Anger: The response is completely devoid of anger. The person is calm, composed, and shows no signs of irritation, frustration, or anger.',
}

toxicity_table = {
    10: 'Extremely Toxic: The response is full of malicious intent, with the person using abusive, hurtful, or degrading language. The message is meant to harm, insult, or manipulate, with no regard for the recipient’s feelings. This level of toxicity can be deeply damaging.',
    9: 'Very Toxic: The response is highly negative and harmful, with the person using strong, offensive language or making demeaning comments. The tone is hostile and meant to inflict emotional harm or manipulate the situation aggressively.',
    8: 'Toxic: The response contains a significant amount of negativity and hostility. The person may use sharp, biting language or make sarcastic, cutting remarks designed to hurt or belittle the recipient.',
    7: 'Quite Toxic: The response shows a clear intent to be hurtful or manipulative. The person’s language is harsh, critical, or overly sarcastic, with a tone that is disrespectful and potentially harmful.',
    6: 'Moderately Toxic: The response is somewhat toxic, with the person using language that is sharp, critical, or sarcastic. While not overtly abusive, the tone is negative and may be intended to manipulate or belittle the recipient.',
    5: 'Slightly Toxic: The response contains mild elements of toxicity. The person might use a sarcastic or critical tone, but the negativity is not overwhelming. There’s a clear intention to be slightly hurtful or manipulative, but it’s more subtle.',
    4: 'Barely Toxic: The response has a slight hint of toxicity. The person may be somewhat critical or sarcastic, but the overall tone is more negative than supportive. The toxicity is minimal and may not be immediately noticeable.',
    3: 'Minimal Toxicity: The response shows just a trace of toxicity. The person might express mild sarcasm or criticism, but it’s very understated and likely not intended to cause significant harm.',
    2: 'Very Little Toxicity: The response indicates only a very small amount of toxicity. The person may be slightly negative or critical, but the tone is mostly neutral with just a faint hint of negativity.',
    1: 'Almost No Toxicity: The response shows negligible toxicity. The person is generally neutral or slightly negative but does not use harmful or manipulative language. The tone is largely respectful.',
    0: 'No Toxicity: The response is completely free of any toxicity. The person’s language is positive, respectful, and supportive, with no intent to harm, manipulate, or belittle the recipient.',
}


@dataclass
class DialogueMood:
    toxicity: int = field(default_factory=lambda: 1)
    anger: int = field(default_factory=lambda: 1)
    joy: int = field(default_factory=lambda: 3)

    def __str__(self):
        return f'''
* {toxicity_table[int(self.toxicity)]}
* {anger_table[int(self.anger)]}
* {joy_table[int(self.joy)]}
'''

    def headers_only(self):
        return f'''
* {toxicity_table[int(self.toxicity)].split(':')[0]}
* {anger_table[int(self.anger)].split(':')[0]} 
* {joy_table[int(self.joy)].split(':')[0]}
'''
