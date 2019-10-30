import requests
from IPython.display import display, clear_output
import ipywidgets as widgets
import asyncio

class Updater(object):
    '''Designed to initiate a streaming/updating task for a chart object. It repeatedly calls the plot
    function, thus the plot coming in should represent the most recent data.
    Params:
        plot - plot(), Chart object, gets passed to IPython display. 
        activated - Bool, whether the chart should initiate as streaming or static. 
        rate - Int, slider value, for the starting delay in updating. 
        **kwargs - Dict, passed to Output() object for displaying the chart. 

    Returns: 
        Updater() - call to Updater().run() begins the procedure. 
    '''

    def __init__(self, plot, activated=False, rate=5, height='500px', **kwargs):
        '''It is important to specify a height for the Output() object so that on update, the
        IPython display need not rescale. This allows the chart to flicker but not change size. 
        '''
        self.out = widgets.Output(layout=widgets.Layout(border='1px solid grey',
                                                        height=height,
                                                        #justify_content='space_around',
                                                        align_items='center',
                                                        **kwargs))
        self.plot = plot()
        self.activated = not activated # Flip activated, to unflip and initialize later. 
        self.rate = rate
        self.collection = self._construct()
        
    def _construct(self):
        '''Construct the widget objects. Changes to appearance of the task bar above the plot
        should go here.
        '''
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
        '''Update widgets.Output() display object.
        Returns:
            widgets collection - original widgets, updated plot. 
        '''
        with self.out:
            self.out.clear_output(wait=True)
            # Plot should return chart object
            display(self.plot)
        return widgets.VBox([self.collection, self.out])

    # Coroutines related
    def _on_check(self, c):
        '''On widget state change, widget.observe() produces 3 dictionaries with matching keys. 
        The first is the releasing of the widget resource and contains no pertinent information. 
        The second contains the actual value change, and the third is the subsequent locking. 
        On checkbox check, we initiate a coroutine to update repeatedly. 
        '''
        if c['name'] == 'value' and c['old'] != c['new']:
            if c['new']:
                asyncio.Task(self.update_loop())
            else:
                asyncio.Task(self.update())

    async def update_loop(self):
        '''Awaitable coroutine for the loop. `await` frees the kernel while it sleeps.
        Method monitors for a change in the widget state to terminate.
        '''
        while True:
            display(self._main())
            await asyncio.sleep(self.collection.children[1].value)
            if self.collection.children[0].value == False:
                break

    async def update(self):
        '''Coroutine for static rendering of chart. Must be awaitable, or in other words, there
        must be a release of the kernel, thus sleep(0) is used.
        '''
        display(self._main())
        await asyncio.sleep(0)

    def run(self):
        '''Begins widget based coroutine that monitors the widget state for changes. If the kernel
        is freed, this task can resume allowing state updates within previously information-closed 
        loops. Note: On observe, no change has occured to the widget. As a result we manually toggle 
        the widget forcing the tasks to begin. Reversal of self.activated = not activated.
        '''
        self.collection.children[0].observe(self._on_check)
        self.collection.children[0].value = not self.collection.children[0].value
