# Assets

This folder contains media assets for the project README and documentation.

## Creating the Demo GIF

To create `demo.gif`:

1. **Open a Jupyter notebook** with luxin installed
2. **Run an example** like:
   ```python
   from luxin import TrackedDataFrame
   
   df = TrackedDataFrame({
       'category': ['Electronics', 'Electronics', 'Clothing', 'Clothing', 'Food', 'Food'],
       'product': ['Laptop', 'Mouse', 'Shirt', 'Pants', 'Apple', 'Banana'],
       'sales': [1000, 50, 30, 45, 2, 1],
       'profit': [200, 10, 10, 15, 0.5, 0.3]
   })
   
   agg = df.groupby(['category']).agg({'sales': 'sum', 'profit': 'sum'})
   agg.show_drill_table()
   ```

3. **Record the screen** while:
   - Showing the aggregated table
   - Clicking on a few rows to reveal detail panels
   - Closing the panels
   - Clicking on different rows

4. **Convert to GIF** using tools like:
   - **macOS**: QuickTime Player + [Gifski](https://gif.ski/)
   - **Online**: [ezgif.com](https://ezgif.com/)
   - **Command line**: `ffmpeg -i demo.mov -vf "fps=10,scale=800:-1:flags=lanczos" -c:v gif demo.gif`

5. **Optimize the GIF**:
   - Keep it under 5MB for GitHub
   - Aim for 800-1000px width
   - 5-10 seconds duration
   - 10-15 fps is usually enough

6. **Save as** `demo.gif` in this folder

## Alternative: Video

You can also use MP4 video:

```markdown
https://user-images.githubusercontent.com/YOUR_USER_ID/YOUR_VIDEO.mp4
```

Upload via GitHub issue/PR and copy the URL.

