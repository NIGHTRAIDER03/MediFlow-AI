import imageio
import os

print("Starting GIF conversion...")
reader = imageio.get_reader('docs/demo.webm')
fps = reader.get_meta_data()['fps']

# We can reduce fps and size to make the gif smaller and process faster
writer = imageio.get_writer('docs/demo.gif', fps=10)

count = 0
for i, im in enumerate(reader):
    # keep 10 frames per second
    if i % int(fps / 10) == 0:
        # Resize image for smaller GIF size (optional, but good for READMEs)
        # We can just write the frame directly if we don't resize, but scaling is better.
        # Let's just write it directly to keep it simple, or use cv2 to resize if needed.
        # But we don't have cv2. We'll just write the raw frame.
        writer.append_data(im)
        count += 1
        if count % 50 == 0:
            print(f"Processed {count} frames...")

writer.close()
print("Saved docs/demo.gif")
