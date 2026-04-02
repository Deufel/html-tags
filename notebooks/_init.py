import marimo

__generated_with = "0.22.0"
app = marimo.App()

with app.setup:

    def __getattr__(name):
        return mktag(name.rstrip('_').replace('_', '-'))




@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
