import imageio
import numpy as np

video_path = r"C:\Users\scien\.gemini\antigravity-ide\brain\684d832b-f096-417c-8e0a-840ab0a4cf78\mediflow_ai_test_run_1784055288366.webp"
reader = imageio.get_reader(video_path)
meta = reader.get_meta_data()
print("Metadata:", meta)

frames = []
for i, frame in enumerate(reader):
    frames.append(frame)
    if i % 100 == 0:
        print(f"Read {i} frames")

print(f"Total frames: {len(frames)}")
