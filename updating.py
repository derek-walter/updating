import requests
from IPython.display import display, clear_output
import ipywidgets as widgets
import asyncio

class Updater(object):

    def __init__(self, plot, activated=False, rate=5, height='500px', **kwargs):
        self.out = widgets.Output(layout=widgets.Layout(border='1px solid grey',
                                                        height=height,
                                                        #justify_content='space_around',
                                                        align_items='center',
                                                        **kwargs))
        self.plot = plot()
        self.activated = not activated
        self.rate = rate
        self.collection = self._construct()
        
    def _construct(self):
        items_layout = widgets.Layout(width='70%')

        box_layout = widgets.Layout(display='flex',
                                    border='1px solid grey',
                                    align_items='stretch',
                                    width='100%')

        checkbox = widgets.Checkbox(value=self.activated, layout=items_layout, description='Update')
        slider = widgets.IntSlider(min=1, max=60, step=1, value=self.rate, continuous_update=False, layout=items_layout, description='Delay')
        collection = widgets.HBox([checkbox, slider], layout=box_layout)
        return collection

    def _main(self):
        # Return widgets and the updated output widget
        with self.out:
            self.out.clear_output(wait=True)
            # Plot should return chart object
            display(self.plot)
        return widgets.VBox([self.collection, self.out])

    # Coroutines related
    def _on_check(self, c):
        if c['name'] == 'value' and c['old'] != c['new']:
            if c['new']:
                asyncio.Task(self.update_loop())
            else:
                asyncio.Task(self.update())

    async def update_loop(self):
        while True:
            display(self._main())
            await asyncio.sleep(self.collection.children[1].value)
            if self.collection.children[0].value == False:
                break

    async def update(self):
        display(self._main())
        await asyncio.sleep(0) # Free kernel

    def run(self):
        self.collection.children[0].observe(self._on_check)
        self.collection.children[0].value = not self.collection.children[0].value
