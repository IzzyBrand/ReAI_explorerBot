# ReAI_explorerBot

This was the final Project for the Reintegrating AI class at Brown (CS2951x).

## Abstract

In this project, we explored machine learning in an embodied setting in order to investigate the unique challenges and opportunities presented by placing a learning agent in the real world. We developed a robot, ExplorerBot, capable of navigating the environment and avoiding obstacles. ExplorerBot, a two-wheeled robot constructed from 3D-printed parts and standard low-cost electronics, served as a test-bed for two primary control policies: the first was a hand-coded policy based on values from ExplorerBot's time-of-flight (ToF) distance sensors; the second was a learned policy based on deep Q-learning. We tested deep Q-learning on input from a forward facing camera, but after extensive training this approach failed to produce desirable navigation behavior. We hypothesize that this is due to the fact that typical deep Q-networks (DQN) require on the order of millions of samples, which we were unable to collect due to limitations of sampling frequency in the real world. To validate our DQN implementation, we then trained on input from the ToF sensors, a fundamentally easier problem. Although this DQN-ToF policy was not optimal in a reward-collection test, it allowed ExplorerBot to reliably navigate in its environment without crashing.

 * The paper and poster can be found in the ` paper/ ` folder. 
 * Information on the robot and STL files can be found in ` hardware.md `
 * Information on setting up the software can be found in ` depends.md `
 
The ` master ` branch contains our failed attempt to train the DQN on camera images. The ` tof_dqn ` branch contains our successful attempt to train the DQN based on ToF distance sensors to avoid obstancles in the environment. The TensorFlow model in ` models/tof_model_robot_history_slower.ckpt ` contains the final successful network parameters that were trained in a 9-hour session. 
