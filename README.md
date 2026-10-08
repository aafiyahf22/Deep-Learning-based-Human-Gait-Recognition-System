# Deep-Learning-based-Human-Gait-Recognition-System
Gait recognition is a great Biometric technique that can detect a person without any
physical contact between the person and the system, or the person having to do anything.
However, it is susceptible to real-world conditions like carrying objects, changing clothes
and different walking environments, which result in declining recognition rate and
challenging task for strong identification. In an attempt to address these shortcomings, this
thesis proposes a gait recognition system which combines space and time feature learning
to enhance the overall performance when confronted with non-constrained scenarios.Three
different conditions, namely normal walk, normal walk with a bag and walking with a coat
were used, with a custom dataset of 30 subjects. The scenarios were being designed to
emulate real-life practical differences with surveillance systems. The video data recorded
was preprocessed into a text file and then converted to frames for feature extraction and
model training. The model proposed here extracts high-level spatial features from frames
using an EfficientNet and temporal motion patterns across the sequences using a
Bidirectional Long Short-Term Memory (BiLSTM) network. This Hybrid CNN-BiLSTM
architecture has been demonstrated to learn appearance-based and even motion-based gait
features, which further enhances the inter-personal gait classification performance. Results
of the experiment prove that the proposed technique is robust and performs consistently
and correctly in any walk condition, even with changing types of clothing and carrying
items. The system is able to extract discriminative gait patterns which are well suited to
various real-world applications including intelligent surveillance, security monitoring and
biometric authentication.
