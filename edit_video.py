import imageio
import numpy as np
import os

video_path = r"C:\Users\scien\.gemini\antigravity-ide\brain\684d832b-f096-417c-8e0a-840ab0a4cf78\mediflow_ai_test_run_1784055288366.webp"
output_path = r"C:\interview\docs\demo_v5.gif"

print(f"Reading {video_path}...")
reader = imageio.get_reader(video_path)
meta = reader.get_meta_data()
fps = meta.get('fps', 10)

writer = imageio.get_writer(output_path, fps=fps)

last_kept_frame = None
kept_count = 0
dropped_count = 0
static_run = 0

for i, frame in enumerate(reader):
    if last_kept_frame is None:
        writer.append_data(frame)
        last_kept_frame = frame
        kept_count += 1
        continue
    
    # Calculate difference
    diff = np.mean(np.abs(frame.astype(np.float32) - last_kept_frame.astype(np.float32)))
    
    # If the frame is very similar to the last kept frame (e.g. diff < 2.0)
    if diff < 1.0:
        static_run += 1
        # Keep 1 frame every 10 frames of static content (speeds up waiting time 10x)
        # But if it's the AI loading, we just want to speed it up
        if static_run % 10 == 0:
            writer.append_data(frame)
            kept_count += 1
        else:
            dropped_count += 1
    else:
        static_run = 0
        writer.append_data(frame)
        last_kept_frame = frame
        kept_count += 1
        
    if i % 100 == 0:
        print(f"Processed {i} frames... (Kept: {kept_count}, Dropped: {dropped_count})")

writer.close()
print(f"Done! Saved to {output_path}")
print(f"Total kept: {kept_count}, Total dropped: {dropped_count}")
