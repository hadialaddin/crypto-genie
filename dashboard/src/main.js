// Datafeed implementation, will be added later
import Datafeed from './datafeed.js';

window.tvWidget = new TradingView.widget({
	symbol: 'Bitfinex:BTC/USD', // default symbol
	interval: '1D', // default interval
	fullscreen: true, // displays the chart in the fullscreen mode
	container: 'tv_chart_container',
	datafeed: Datafeed,
	library_path: './charting_library_clonned_data/charting_library/',
});


window.tvWidget.onChartReady(() => {
	let crosshairValue;
	
	const crosshairMovedHandler = (params) => {
		crosshairValue = params;
	};
	
	// This is not working
	tvWidget.activeChart().crossHairMoved().subscribe(null, crosshairMovedHandler);
	
	// And this is not working too (and I tried them separately, also not working)
	tvWidget.subscribe('mouse_down', () => {
		const mouseUpHandler = () => {
			console.log(crosshairValue);
			window.crosshairValues.push(crosshairValue);
			tvWidget.unsubscribe('mouse_up', mouseUpHandler);
		};

		tvWidget.subscribe('mouse_up', mouseUpHandler);
	});
	
});