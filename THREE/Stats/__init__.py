"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""


class _Panel:
	def __init__(self, name, fg, bg ):
		min = Infinity
		max = 0
		round = Math.round
		PR = round( window.devicePixelRatio || 1 )

		WIDTH = 80 * PR
		HEIGHT = 48 * PR
		TEXT_X = 3 * PR
		TEXT_Y = 2 * PR
		GRAPH_X = 3 * PR
		GRAPH_Y = 15 * PR
		GRAPH_WIDTH = 74 * PR
		GRAPH_HEIGHT = 30 * PR

		var canvas = document.createElement( 'canvas' )
		canvas.width = WIDTH
		canvas.height = HEIGHT
		canvas.style.cssText = 'width:80px;height:48px'

		var context = canvas.getContext( '2d' )
		context.font = 'bold ' + ( 9 * PR ) + 'px Helvetica,Arial,sans-serif'
		context.textBaseline = 'top'

		context.fillStyle = bg
		context.fillRect( 0, 0, WIDTH, HEIGHT )

		context.fillStyle = fg
		context.fillText( name, TEXT_X, TEXT_Y )
		context.fillRect( GRAPH_X, GRAPH_Y, GRAPH_WIDTH, GRAPH_HEIGHT )

		context.fillStyle = bg
		context.globalAlpha = 0.9
		context.fillRect( GRAPH_X, GRAPH_Y, GRAPH_WIDTH, GRAPH_HEIGHT )

	def update(self, value, maxValue ):
		mn = Math.min( min, value )
		mx = Math.max( max, value )

		context.fillStyle = bg
		context.globalAlpha = 1
		context.fillRect( 0, 0, WIDTH, GRAPH_Y )
		context.fillStyle = fg
		context.fillText( round( value ) + ' ' + name + ' (' + round( mn ) + '-' + round( mx ) + ')', TEXT_X, TEXT_Y )

		context.drawImage( canvas, GRAPH_X + PR, GRAPH_Y, GRAPH_WIDTH - PR, GRAPH_HEIGHT, GRAPH_X, GRAPH_Y, GRAPH_WIDTH - PR, GRAPH_HEIGHT )

		context.fillRect( GRAPH_X + GRAPH_WIDTH - PR, GRAPH_Y, PR, GRAPH_HEIGHT )

		context.fillStyle = bg
		context.globalAlpha = 0.9
		context.fillRect( GRAPH_X + GRAPH_WIDTH - PR, GRAPH_Y, PR, round( ( 1 - ( value / maxValue ) ) * GRAPH_HEIGHT ) )

		
class Stats:
	REVISION = 16

	def __init__(self, options):
		var container = document.createElement( 'div' )
		container.style.cssText = 'position:fixed;top:0;left:0;cursor:pointer;opacity:0.9;z-index:10000'
		container.addEventListener( 'click', function ( event ) {
			event.preventDefault()
			showPanel( ++ mode % container.children.length )

		}, false )

		# //

		def addPanel( panel ):
			container.appendChild( panel.dom )
			return panel

		def showPanel( id ):
			for i = 0; i < container.children.length; i ++ ) {
				container.children[ i ].style.display = i === id ? 'block' : 'none'

			mode = id

		# //

		self.beginTime = time.clock()
		self.prevTime = beginTime
		self.frames = 0

		fpsPanel = addPanel( _Panel( 'FPS', '#0ff', '#002' ) )
		msPanel = addPanel( _Panel( 'MS', '#0f0', '#020' ) )
		memPanel = addPanel( _Panel( 'MB', '#f08', '#201' ) )

		showPanel( 0 )

	def begin(self):
		self.beginTime = time.clock()

	def end(self):
		self.frames += 1
		time = time.clock()

		msPanel.update( time - beginTime, 200 )

		if time >= prevTime + 1000:
			fpsPanel.update( ( frames * 1000 ) / ( time - prevTime ), 100 )

			prevTime = time
			frames = 0

			if memPanel:
				memory = performance.memory
				memPanel.update( memory.usedJSHeapSize / 1048576, memory.jsHeapSizeLimit / 1048576 )

			return time

	def update(self):
		beginTime = this.end()

