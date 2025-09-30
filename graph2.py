import turtle as tt
import tkinter as tk
from tkinter import messagebox, simpledialog, font, ttk
import time, uuid, math, subprocess, os
from typing import Literal, Callable
from usableScreenSize import get_usable_screen_size



class Graph():
  def __init__(self, Tt: tt):
    self.tt = Tt
    self.screen = Tt.Screen()
    self.max_w, self.max_h, self.usable_w, self.usable_h = get_usable_screen_size()
    self.initial_w = 2*self.usable_w/3
    self.initial_h = 2*self.usable_h/3
    self.screen.setup(self.initial_w, self.initial_h)
    self.screen.mode("standard")
    self.screen.tracer(0, 0)
    self.root: tk.Tk = self.screen._root # Get the Tk root from tt
    self.style = ttk.Style(self.root)
    self.style.theme_use('clam')
    self.writer = self.tt.Turtle(visible=False)
    self.callback: Callable | None = None
    self.functions_list_objs: list[HelperFunction] = []

    self.update()
    self.popups = GraphPopups(self)
    self.model = GraphModel(self)
    self.gui = GraphGUI(self)
    self.initial_mid_n = self.gui.mid_n
    self.objects_class = GraphObjects(self)
    self.math = GraphMath(self)
    self.view = GraphView(self)
    self.controller = GraphController(self)
    self.functions = GraphFunctions(self)
    self.executableHandler = GraphExecutableHandler(self)

  def getWindowSize(self):
    return (self.screen.window_width(), self.screen.window_height())

  def update(self):
    self.max_w, self.max_h, self.usable_w, self.usable_h = get_usable_screen_size()

class GraphModel():
  def __init__(self, graph: Graph):
    self.graph = graph
    self.busy = False
    self.scale_x = 8.0
    self.scale_y = 8.0
    self.p_pensize = 3
    self.s_pensize = 2
    self.t_pensize = 1
    self.max_unit_w = 60.0
    self.max_unit_w_p = 40.0
    self.max_unit_h_p = 0.0
    self.t_x = 0.0
    self.t_y = 0.0
    self.limit = 6
    self.mark_added_object_onclick = False
    self.graph.style.configure(
      "Gray.Horizontal.TScale",
      troughcolor="#D0D0D0", # Light gray background track
      background="#808080", # Medium gray slider button
      sliderthickness=20 # (Optional) Make slider a bit thicker for modern look
    )
    self.graph.style.configure(
      "Modified.Horizontal.TScale",
      sliderthickness=20 # (Optional) Make slider a bit thicker for modern look
    )
    self.graph.style.configure(
      "RedButton.TButton",
      background="#F44336", # Medium red slider button
    )
    self.graph.style.configure(
      "GreenButton.TButton",
      background="#4CAF50", # Medium green slider button
    )
    self.graph.style.configure(
      "BlueButton.TButton",
      background="#2196F3", # Medium blue slider button
    )

  def mod(self, num, modulus):
    return num - (num // modulus) * modulus

  def splice(self, array: list, index = 0, apply_mod=False):
    l = len(array)
    if l <= 0: return []
    if index >= l:
      if not apply_mod: return []
      index = self.mod(index, l)
    if index < 0:
      if not apply_mod: return []
      index = self.mod(index, l)
    a = array[:index]
    b = array[index+1:]
    return a + b

  def setScaleX(self, number:float):
    sgn = self.getSgn(number)
    if abs(self.scale_x) < 1:
      self.scale_x = sgn * max(abs(number), 1e-100)
    else:
      self.scale_x = sgn * min(abs(number), 1e100)

    if self.graph.gui:
      self.graph.gui.updateMenuBar()

  def setScaleY(self, number:float):
    sgn = self.getSgn(number)
    if abs(self.scale_y) < 1:
      self.scale_y = sgn * max(abs(number), 1e-100)
    else:
      self.scale_y = sgn * min(abs(number), 1e100)

    if self.graph.gui:
      self.graph.gui.updateMenuBar()

  def translateX(self, number: float):
    n_t_x = self.t_x + number
    sgn = self.getSgn(n_t_x)
    if abs(n_t_x) < 1:
      self.t_x = sgn * max(abs(n_t_x), 1e-100)
    else:
      self.t_x = sgn * min(abs(n_t_x), 1e100)

    if self.graph.gui:
      self.graph.gui.updateMenuBar()

  def translateY(self, number: float):
    n_t_y = self.t_y + number
    sgn = self.getSgn(n_t_y)
    if abs(n_t_y) < 1:
      self.t_y = sgn * max(abs(n_t_y), 1e-100)
    else:
      self.t_y = sgn * min(abs(n_t_y), 1e100)

    if self.graph.gui:
      self.graph.gui.updateMenuBar()

  def getSgn(self, number: float):
    if number >= 0: return 1
    else: return -1


class GraphGUI():
  def __init__(self, graph: Graph):
    self.graph = graph
    self.root = self.graph.root
    self.menu_bar = tk.Menu(self.root)
    self.root.config(menu=self.menu_bar)
    self.mid_n = 35
    self.show_axes = tk.BooleanVar(value=True)
    self.show_units = tk.BooleanVar(value=True)
    self.show_grid = tk.BooleanVar(value=True)
    self.compute_number_value = 0
    self.turtle_choice = tk.StringVar(value="None")
    self.half_grid_number_value = 20
    self.grid_number_value = self.half_grid_number_value * 2 + 1
    self.callables: list[Callable] = []
    self.zoom_step = 1

    self.updateMenuBar()
    self.drawAxes()


  def updateMenuBar(self):
    self.graph.popups.closeAllPopups() # Effectively closes all non-menu popups
    self.menu_bar.delete(1, tk.END)

    # Main menu items
    self.addCascade(self.menu_bar, "File")
    self.addCascade(self.menu_bar, "Edit")
    self.settings_menu = self.addCascade(self.menu_bar, "Settings")
    self.functions_menu = self.addCascade(self.menu_bar, "Functions")
    # self.addSeparators(self.mid_n)
    self.addCascade(self.menu_bar, "Help")
    self.addCascade(self.menu_bar, "Clear screen")
    self.menu_bar.add_command(label="Set zoom step", command=self.setZoomStep)
    self.menu_bar.add_command(label="Zoom in", command=self.zoomIn)
    self.menu_bar.add_command(label="Zoom out", command=self.zoomOut)
    self.menu_bar.add_command(label="Reset Zoom", command=self.resetZoom)
    self.menu_bar.add_command(label="Center", command=self.center)

    # Settings menu items
    self.axes_menu = self.addCascade(self.settings_menu, "Axes")
    self.axes_menu.add_checkbutton(label="Show Axes", variable=self.show_axes, command=self.checkAxes)
    self.axes_menu.add_checkbutton(label="Show Units", variable=self.show_units, command=self.checkUnits)
    self.axes_menu.add_checkbutton(label="Show Grid", variable=self.show_grid, command=self.checkGrid)

    self.compute_number = self.addCascade(self.settings_menu, "Compute Number")
    self.compute_number_edit = self.compute_number.add_command(label="Edit", command=self.editComputeNumber)
    self.compute_number_view = self.compute_number.add_command(label="View", command=self.viewComputeNumber)

    self.settings_menu.add_command(label="Set absolute X scale value", command=self.setAbsXScale)
    self.settings_menu.add_command(label="Set absolute Y scale value", command=self.setAbsYScale)
    self.settings_menu.add_command(label="Set absolute X translation value", command=self.setAbsXTrans)
    self.settings_menu.add_command(label="Set absolute Y translation value", command=self.setAbsYTrans)

    self.turtle_to_add_onclick = self.addCascade(self.settings_menu, "Object to add on Screen Click")
    self.turtle_to_add_onclick.add_radiobutton(label="Point", variable=self.turtle_choice, value="Point",\
                                                command=self.setTurtleToAddOnClick)
    self.turtle_to_add_onclick.add_radiobutton(label="Line", variable=self.turtle_choice, value="Line",\
                                                command=self.setTurtleToAddOnClick)
    self.turtle_to_add_onclick.add_radiobutton(label="None", variable=self.turtle_choice, value="None",\
                                                command=self.setTurtleToAddOnClick)

    # Function List
    self.function_list_menu = self.addCascade(self.functions_menu, "Functions list")
    # self.callCallables()

    # # Function menu items
    # self.active_functions_menu = self.addCascade(self.menu_bar, "Active functions")
    # l = len(self.graph.functions_list_objs)
    # for i in range(l):
    #   obj = self.graph.functions_list_objs[i]
    #   if i == 0:
    #     self.active_functions_menu.add_command(label="Clear All Active Functions", command=obj.accessory.removeAllFunctions)
    #     self.active_functions_menu.add_command(label="Clear Selected Active Functions", command=obj.accessory.removeFunctions)
    #   obj.updateFunctionMenuBar()

    self.addCascade(self.menu_bar, f"Zoom step: {self.zoom_step}\
                    Scale: {round(self.graph.model.scale_x, 4)}, {round(self.graph.model.scale_x, 4)}\
                    Translation: {round(self.graph.model.t_x, 4)}, {round(self.graph.model.t_y, 4)}")

  def addSeparators(self, n=1):
    for i in range(n):
      self.menu_bar.add_separator()

  def addCascade(self, menu: tk.Menu, input_label:str):
    m = tk.Menu(menu, tearoff=0)
    menu.add_cascade(menu=m, label=input_label)
    return m

  def callCallables(self):
    for callable in self.callables: # Callables (Functions)
      callable()

  def setAbsXScale(self):
    tmp = simpledialog.askfloat(title="Scale X value", prompt="Set absolute value for X scale", minvalue=0)
    if tmp is not None:
      if tmp == 0: tmp = 1
      self.graph.model.setScaleX(tmp)

  def setAbsYScale(self):
    tmp = simpledialog.askfloat(title="Scale Y value", prompt="Set absolute value for Y scale", minvalue=0)
    if tmp is not None:
      if tmp == 0: tmp = 1
      self.graph.model.setScaleY(tmp)

  def setAbsXTrans(self):
    tmp = simpledialog.askfloat(title="X translation value", prompt="Set absolute value for X translation")
    if tmp is not None:
      self.graph.model.translateX(-self.graph.model.t_x + tmp)

  def setAbsYTrans(self):
    tmp = simpledialog.askfloat(title="Y translation value", prompt="Set absolute value for Y translation")
    if tmp is not None:
      self.graph.model.translateY(-self.graph.model.t_y + tmp)

  def zoomIn(self):
    self.graph.model.setScaleX(self.graph.model.scale_x / self.zoom_step)
    self.graph.model.setScaleY(self.graph.model.scale_y / self.zoom_step)

  def zoomOut(self):
    self.graph.model.setScaleX(self.graph.model.scale_x * self.zoom_step)
    self.graph.model.setScaleY(self.graph.model.scale_y * self.zoom_step)

  def resetZoom(self):
    self.graph.model.setScaleX(1)
    self.graph.model.setScaleY(1)


  def center(self):
    self.graph.model.translateX(-self.graph.model.t_x)
    self.graph.model.translateY(-self.graph.model.t_y)

  def setZoomStep(self):
    tmp = simpledialog.askfloat(title="Zoom step", prompt="Set the zoom step value",\
                                initialvalue=self.zoom_step, minvalue=1)
    if tmp is not None:
      self.zoom_step = tmp

  def drawAxes(self):
    w, h = self.graph.getWindowSize()
    # x (horizontal axis)
    x = Line(self.graph, (-w/2, 0)).extend((w/2, 0))
    x.name = "gridX"
    x.no_translate = True

    # y (vertical axis)
    y = Line(self.graph, (0, h/2)).extend((0, -h/2))
    y.name = "gridY"
    y.no_translate = True

  def checkAxes(self):
    if self.show_axes.get():
      self.drawAxes()
    self.graph.controller.updateController()

  def checkUnits(self):
    self.graph.controller.updateController()

  def checkGrid(self):
    self.graph.controller.updateController()

  def editComputeNumber(self):
    tmp = simpledialog.askinteger(title="Compute Number", prompt = "Input compute number",\
                                  initialvalue=self.compute_number_value, minvalue = 0, parent=self.compute_number)
    if tmp is not None: self.compute_number_value = tmp

  def viewComputeNumber(self):
    messagebox.showinfo(title="Compute number value", message=f"The compute number value is\
                        {self.compute_number_value}")

  def setTurtleToAddOnClick(self):...

  def printGeometry(self):
    print(self.root.geometry())

  def getGeometryParams(self):
    geo = self.root.geometry()
    tmp = geo.split("x")
    tmp = [tmp[0]] + tmp[1].split("+")
    return [int(i) for i in tmp]


class GraphObjects():
  objects = []

  def __init__(self, graph: Graph):
    self.graph = graph

  def clear(self):
    GraphObjects.objects.clear()
    # self.graph.setScreenDragObj()



class Point():
  def __init__(self, graph: Graph, origin: tuple[float, float] = (0.0, 0.0), radius:\
               tuple[float, float] = (0.1, 0.1), outline = 0.0, color = "black",\
                fillColor = "black", speed: float = 0.0):
    GraphObjects.objects.append(self)
    self.graph = graph
    self.type = "Point"
    self.name = ""
    self.shape = self.graph.tt.Turtle()
    self.id = uuid.uuid4().int
    self.show = True
    self.origin = origin
    self.radius = radius
    self.outline = outline
    self.color = color
    self.fillColor = fillColor
    self.speed = speed
    self.deleted = False
    self.mark = False
    self.no_translate = False


  def draw(self, t_x = 0.0, t_y = 0.0):
    if self.show:
      if self.no_translate:
        t_x = 0.0
        t_y = 0.0
      self.shape.ht()
      self.shape.pu()
      self.shape.speed(0)
      self.shape.goto(self.origin[0] + t_x, self.origin[1] + t_y)
      self.shape.speed(self.speed)
      self.shape.shape("circle")
      self.shape.shapesize(*self.radius, self.outline)
      self.shape.resizemode("user")
      self.shape.color(self.color)
      self.shape.fillcolor(self.fillColor)
      self.shape.begin_fill()
      self.shape.end_fill()
      self.shape.st()
      if self.mark: self.deleted = True
    return self

  def update(self, origin: tuple[float, float] | None = None, radius:\
             tuple[float, float] | None = None, outline: float | None = None,\
              color: str | None = None, fillColor: str | None= None, speed: float | None = None):
    self.shape.clear()
    if origin is not None: self.origin = origin
    if radius is not None: self.radius = radius
    if outline is not None: self.outline = outline
    if color is not None: self.color = color
    if fillColor is not None: self.fillColor = fillColor
    if speed is not None: self.speed = speed
    return self

  def hide(self):
    self.shape.clear()
    self.shape.pu()
    self.shape.ht()
    return self

  def importShape(self, pointImport: list):
    type, o, r, outl, col, fillCol, speed = pointImport
    if (type == "Point"):
      self.origin = o
      self.radius = r
      self.outline = outl
      self.color = col
      self.fillColor = fillCol
      self.speed = speed
    return self

  def exportShape(self):
   return [
      self.type,
      self.origin,
      self.radius,
      self.outline,
      self.color,
      self.fillColor,
      self.speed
   ]

  def __del__(self):...
    # print(f"Object {self.type} with id {self.id} is about to be deleted")




class Line():
  def __init__(self, graph: Graph, startPoint: tuple[float, float] = (0.0, 0.0),\
               color = "black", speed = 0.0):
    GraphObjects.objects.append(self)
    self.graph = graph
    self.type = "Line"
    self.name = ""
    self.shape = self.graph.tt.Turtle()
    self.id = uuid.uuid4().int
    self.show = True
    self.shapes: list[tuple[float, float]] = []
    self.startPoint = startPoint
    self.shapes.append(self.startPoint)
    self.color = color
    self.speed = speed
    self.deleted = False
    self.mark = False
    self.no_translate = False

  def draw(self, t_x = 0.0, t_y = 0.0):
    # Move the tt to the starting position (startPoint) in non tracing mode
    if self.show:
      if self.no_translate:
        t_x = 0.0
        t_y = 0.0
      self.shape.color(self.color)
      self.shape.ht()
      self.shape.pu()
      self.shape.goto(self.startPoint[0] + t_x, self.startPoint[1] + t_y)
      self.shape.speed(self.speed)
      self.shape.pd()
      l = len(self.shapes)
      for i in range(1, l):
        self.shape.goto(self.shapes[i][0] + t_x, self.shapes[i][1] + t_y)
      if self.mark: self.deleted = True
    return self

  def update(self, startPoint: tuple[float, float] | None = None, color: str | None = None,\
             speed: float | None = None, clearPoints = False):
    self.shape.clear()
    if clearPoints is True:
      self.shapes = []
    l = len(self.shapes)

    if startPoint is not None:
      self.startPoint = startPoint
      if l > 0: self.shapes[0] = self.startPoint
      else: self.shapes.append(self.startPoint)

    if color is not None: self.color = color
    if speed is not None: self.speed = speed
    return self

  def extend(self, endPoint: tuple[float, float]):
    """
    Trace the line from the previous position to the current position (endPoint)
    """
    self.shapes.append(endPoint)
    return self

  def multipleExtend(self, *endPoints:tuple[float, float]):
    l = len(endPoints)
    for i in range(l):
      self.shapes.append(endPoints[i])
    return self

  def hide(self):
    self.shape.clear()
    self.shape.pu()
    return self

  def clearPoints(self):
    self.shape.clear()
    self.shapes = []
    self.shape.pu()
    return self

  def importShape(self, lineImport: list):
    type, col, speed, *points = lineImport
    if (type == "Line"):
      self.startPoint = points[0]
      self.color = col
      self.speed = speed
      self.shapes = points
    return self

  def exportShape(self):
    tmp = [
      self.type,
      self.color,
      self.speed,
    ] + [p for p in self.shapes]

    if len(self.shapes) == 0:
      tmp = tmp + [(0.0, 0.0)]
    return tmp

  def __del__(self):...
    # print(f"Object {self.type} with id {self.id} is about to be deleted")



class GraphMath():
  def __init__(self, graph: Graph):
    self.graph = graph
    self.l_p_x = 0.0
    self.l_p_y = 0.0
    self.d_x = 0.0
    self.d_y = 0.0
    self.updateMode: Literal["onmove"] | Literal["aftermove"] | None = "onmove"

  def execScreenDragStart(self, event):
    p_x, p_y = self.windowTopLeftToCentered((event.x, event.y))
    self.l_p_x = p_x
    self.l_p_y = p_y

  def execScreenDragMotion(self, event):
    if self.updateMode is not None:
      p_x, p_y = self.windowTopLeftToCentered((event.x, event.y))
      d_x = p_x - self.l_p_x
      self.l_p_x = p_x
      d_y = p_y - self.l_p_y
      self.l_p_y = p_y

      if self.updateMode == "onmove":
        self.graph.model.translateX(d_x)
        self.graph.model.translateY(d_y)
        self.graph.controller.updateController()

      elif self.updateMode == "aftermove":
        self.d_x += d_x
        self.d_y += d_y

  def execScreenDragEnd(self, _):
    if self.updateMode is not None and self.updateMode == "aftermove":
      self.graph.model.translateX(self.d_x)
      self.graph.model.translateY(self.d_y)
      self.graph.controller.updateController()
      self.d_x = 0.0
      self.d_y = 0.0

  def getXPointFromX(self, x: float, min_x_point: float):
    return (x / self.graph.model.scale_x) * min_x_point

  def getYPointFromY(self, y: float, min_y_point: float):
    return (y / self.graph.model.scale_y) * min_y_point


  def getXFromXPoint(self, x_point: float, min_x_point: float):
    return (x_point / min_x_point) * self.graph.model.scale_x

  def getYFromYPoint(self, y_point: float, min_y_point: float):
    return (y_point / min_y_point) * self.graph.model.scale_y

  def windowTopLeftToCentered(self, top_left_coords):
    w, h = self.graph.getWindowSize()
    top_left_x, top_left_y = top_left_coords
    centered_x = top_left_x - (w / 2)
    centered_y = (h / 2) - top_left_y
    return (centered_x, centered_y)

  def windowCenteredToTopLeft(self, centered_coords):
    w, h = self.graph.getWindowSize()
    centered_x, centered_y = centered_coords
    top_left_x = centered_x + (w / 2)
    top_left_y = (h / 2) - centered_y
    return (top_left_x, top_left_y)

  def handleDotAndRounding(self, number, base_string: str, w: int, power_sgn: str,\
                           superscripts_string: str, unit_width: int, point_width: int):
    dot_index = base_string.find(".")
    tmp: list[str] = []
    ret_string: str = ""
    pow_int = self.getNumPower(number)

    if dot_index > -1:
      # Allocate space for the decimal point if any
      w = w + point_width
      tmp = base_string.split(".")
      base_string = tmp[0] + "0" + tmp[1]

    n = len(base_string)
    if abs(pow_int) >= self.graph.model.limit:
      ret_string = base_string[0]

    else:
      for i in range(n):
        # Add the decimal point if any (space for it has already been allocated based on its\
        # existence)
        if i == dot_index:
          ret_string = ret_string + "."

        # Add the digits if they don't exceed the max allowed width
        else:
          w = w + unit_width
          if self.graph.model.max_unit_w - w >= 0:
            ret_string = ret_string + base_string[i]

          # Round up the last digit if possible, as the max allowed width has been exceeded
          else:
            last_index = len(ret_string)-1
            if last_index > -1:
              n = int(base_string[:last_index] + base_string[i])
              p = last_index - dot_index
              ret_string = str(round(n, p))

              if dot_index > -1:
                l = len(ret_string)
                tmp_ = ret_string
                ret_string = ""
                for i in range(l):
                  if i == dot_index: ret_string = ret_string + "."
                  else: ret_string = ret_string + tmp_[i]
            break

    multiplier = ""
    if len(superscripts_string) > 0:
      multiplier = "x10" + power_sgn + superscripts_string
    return ret_string + multiplier


  def numberHasE(self, num_string: str, w: int, superscripts_list: list[str], unit_width: int,\
                 superscript_width: int, times_width: int):
    pre_base_pow_list = num_string.replace("e", "x10")
    base_pow_list = pre_base_pow_list.split("x10")
    pow_int = int(base_pow_list[1])
    pow_list = list[str]
    pow_str = ""
    pow_sgn = " "
    superscripts_string = ""

    if pow_int >= 0:
      pow_list = base_pow_list[1].split("+")
    else:
      pow_list = base_pow_list[1].split("-")
      pow_sgn = superscripts_list[11]

    pow_list_len = len(pow_list)
    for i in range(pow_list_len): pow_str = pow_str + pow_list[i]
    pow_str = str(int(pow_str))
    pow_str_len = len(pow_str)
    for i in range(pow_str_len): superscripts_string = superscripts_string +\
      superscripts_list[int(pow_str[i])]
    l = len(superscripts_string)
    w = w + times_width + 2 * unit_width + (l + 1) * superscript_width
    return (base_pow_list[0], w, pow_sgn, superscripts_string)


  def convertToStandard(self, number: float, len: int):
    a = "{:."
    b = "e}"
    res = a + str(len) + b
    return res.format(number)

  def calcPosUnitInterval(self, number: float, pow_int: int):
    pow_int = pow_int - 1
    i = 0
    y = 0.0

    while y < number:
      p = i % 3
      if p == 0:
        pow_int = pow_int + 1
        y = 1 * math.pow(10, pow_int)
      elif p: y = 2 * math.pow(10, pow_int)
      else: y = 5 * math.pow(10, pow_int)
      i = i + 1
    return y

  def calcNegUnitInterval(self, number: float, pow_int: int):
    pow_int = pow_int + 2
    i = 0
    y = 1.0
    l = [0.0, 0.0]

    while y > number:
      p = i % 3
      if p == 0:
        pow_int = pow_int - 1
        y = 5 * math.pow(10, pow_int)
      elif p:
        y = 2 * math.pow(10, pow_int)
      else:
        y = 1 * math.pow(10, pow_int)
      l[1] = l[0]
      l[0] = y
      i = i + 1
    if y == number: return y
    else: return l[1]

  def getNumPower(self, number: float):
    return int("{:.1e}".format(number).split("e")[1])

  def calcUnitInterval(self, number: float):
    sgn = 1
    if number < 0: sgn = -1
    pow_int = self.getNumPower(number)
    if pow_int >= 0: return sgn * self.calcPosUnitInterval(abs(number), pow_int)
    else: return sgn * self.calcNegUnitInterval(abs(number), pow_int)

  def plotNegXAxisUnitLine(self, x, w_p, t_x, t_y):
    l = Line(self.graph, (-x + t_x, w_p + t_y)).extend((-x + t_x, -w_p + t_y))
    l.name = "axis"
    l.mark = True
    l.shape.pensize(self.graph.model.s_pensize)
    l.no_translate = True

  def plotPosXAxisUnitLine(self, x, w_p, t_x, t_y):
    l = Line(self.graph, (x + t_x, w_p + t_y)).extend((x + t_x, -w_p + t_y))
    l.name = "axis"
    l.mark = True
    l.shape.pensize(self.graph.model.s_pensize)
    l.no_translate = True

  def plotNegYAxisUnitLine(self, y, w_p, t_x, t_y):
    l = Line(self.graph, (-w_p + t_x, -y + t_y)).extend((w_p + t_x, -y + t_y))
    l.name = "axis"
    l.mark = True
    l.shape.pensize(self.graph.model.s_pensize)
    l.no_translate = True

  def plotPosYAxisUnitLine(self, y, w_p, t_x, t_y):
    l = Line(self.graph, (-w_p + t_x, y + t_y)).extend((w_p + t_x, y + t_y))
    l.name = "axis"
    l.mark = True
    l.shape.pensize(self.graph.model.s_pensize)
    l.no_translate = True

  def plotNegVGridLine(self, h, x, t_x):
    l = Line(self.graph, (-x + t_x, h/2)).extend((-x + t_x, -h/2))
    l.name = "grid"
    l.mark = True
    l.shape.pensize(self.graph.model.t_pensize)
    l.no_translate = True

  def plotPosVGridLine(self, h, x, t_x):
    l = Line(self.graph, (x + t_x, h/2)).extend((x + t_x, -h/2))
    l.name = "grid"
    l.mark = True
    l.shape.pensize(self.graph.model.t_pensize)
    l.no_translate = True

  def plotPosHGridLine(self, w, y, t_y):
    l = Line(self.graph, (-w/2, y + t_y)).extend((w/2, y + t_y))
    l.name = "grid"
    l.mark = True
    l.shape.pensize(self.graph.model.t_pensize)
    l.no_translate = True

  def plotNegHGridLine(self, w, y, t_y):
    l = Line(self.graph, (-w/2, -y + t_y)).extend((w/2, -y + t_y))
    l.name = "grid"
    l.mark = True
    l.shape.pensize(self.graph.model.t_pensize)
    l.no_translate = True



class GraphView():
  def __init__(self, graph: Graph):
    self.graph = graph
    self.min_x_point = 0
    self.min_y_point = 0
    self.removeArtifacts()

  def removeArtifacts(self):
    for i in range(len(GraphObjects.objects)):
      obj = GraphObjects.objects[i]
      obj.hide()
      obj.shape.ht()
    self.graph.writer.clear()

  def addTurtleOnClick(self, x, y):
    self.graph.objects_class.objects[0].shape
    obj = None
    turtle_choice = self.graph.gui.turtle_choice.get()
    if turtle_choice == "None": return
    elif turtle_choice == "Point": obj = Point(self.graph, (x, y), (1, 1))
    elif turtle_choice == "Line": obj = Line(self.graph, (x, y)).extend((1,1))
    else: return
    if self.graph.model.mark_added_object_onclick: obj.mark = True
    self.graph.controller.updateController()
    return obj

  def updateAxes(self, obj, w:int, h: int):
    w_p = self.graph.model.p_pensize * 2
    t_x = self.graph.model.t_x
    t_y = self.graph.model.t_y

    if obj.name == "gridX":
      if self.graph.gui.show_axes.get():
        d_y = (h/2) - (w_p * 2)
        n_t_y = t_y
        if d_y - abs(t_y) < 0.0:
          if t_y >= 0.0:
            n_t_y = d_y
          else: n_t_y = -d_y
        obj.update((-w/2, n_t_y), clearPoints=True).extend((w/2, n_t_y))
        obj.shape.pensize(self.graph.model.p_pensize)
      else:
        obj.deleted = True

    if obj.name == "gridY":
      if self.graph.gui.show_axes.get():
        d_x = (w/2) - (w_p * 2)
        n_t_x = t_x
        if d_x - abs(t_x) < 0.0:
          if t_x >= 0.0:
            n_t_x = d_x
          else: n_t_x = -d_x
        obj.update((n_t_x, h/2), clearPoints=True).extend((n_t_x, -h/2))
        obj.shape.pensize(self.graph.model.p_pensize)
      else:
        obj.deleted = True

  def updateView(self):
    w, h = self.graph.getWindowSize()
    self.graph.update()
    self.graph.screen.setworldcoordinates(-w//2, -h//2, w//2, h//2)
    self.graph.tt.ht()
    self.graph.writer.ht()
    self.graph.gui.mid_n = int(self.graph.initial_mid_n + ((w - self.graph.initial_w) // 8))
    tmp = []

    if not self.graph.model.busy:
      self.displayUnitsAndGrid(w, h)

      n = len(GraphObjects.objects)
      for i in range(n):
        obj = GraphObjects.objects[i]
        obj.hide()
        self.updateAxes(obj, w, h)

        if not obj.deleted:
          tmp.append(obj)
          obj.draw()

      GraphObjects.objects = tmp
    self.graph.screen.update()
    return (w, h)

  def displayUnit(self, number: float, coords: tuple[float, float], font: font, align: str,\
                  unit_width: int, superscript_width: int, point_width: int, times_width: int):
    number = float(f"{number:.{100}f}")
    superscripts_list = ["\u2070", "\u00B9", "\u00B2", "\u00B3", "\u2074", "\u2075", "\u2076",\
                         "\u2077", "\u2078", "\u2079", "\u207A", "\u207B"]
    w: int = 0
    number_sgn = ""
    # Allocate space for negative sign
    if number < 0:
      w = w + unit_width
      number_sgn = "-"
    # Get the absolute value of the number as a string
    num_string = str(abs(number))
    base_string: str = ""
    power_sgn: str = ""
    superscripts_string = ""
    ret_string: str = ""

    if num_string.find("e") > -1:
      base_string, w, power_sgn, superscripts_string =\
        self.graph.math.numberHasE(num_string, w, superscripts_list, unit_width,\
                                   superscript_width, times_width)
    else:
      l = len(num_string)
      x_w = l * unit_width
      cutoff = 0

      if x_w > self.graph.model.max_unit_w:
        cutoff = self.graph.model.max_unit_w // unit_width
        standard_num_string = self.graph.math.convertToStandard(abs(number), cutoff)
        base_string, w, power_sgn, superscripts_string =\
          self.graph.math.numberHasE(standard_num_string, w, superscripts_list, unit_width,\
                                     superscript_width, times_width)

      else: base_string = num_string
    ret_string = number_sgn +\
      self.graph.math.handleDotAndRounding(number, base_string, w, power_sgn,\
                                           superscripts_string, unit_width, point_width)

    self.graph.writer.penup()
    self.graph.writer.goto(coords)
    self.graph.writer.pensize(self.graph.model.t_pensize)
    self.graph.writer.write(ret_string, align=align, font=font)

  def displayUnitsAndGrid(self, w: int, h: int):
    if self.graph.gui.show_units.get(): self.removeArtifacts()
    else: self.graph.writer.clear()

    unitFont = font.Font(family="Arial", size=10, weight="bold", slant="italic")
    font_height = unitFont.metrics("linespace")

    unit = "0"
    unit_width = unitFont.measure(unit)
    superscript = "\u2070"
    superscript_width = unitFont.measure(superscript)
    point = "."
    point_width = unitFont.measure(point)
    times = "x"
    times_width = unitFont.measure(times)

    tmp_val = (self.graph.model.max_unit_w + 2 * self.graph.model.max_unit_w_p) - font_height
    if tmp_val > 0:
      self.graph.model.max_unit_h_p = tmp_val / 2
    else: self.graph.model.max_unit_h_p = 0

    w_p = self.graph.model.p_pensize * 2
    t_x = self.graph.model.t_x
    t_y = self.graph.model.t_y

    self.min_x_point = ((self.graph.model.max_unit_w / 2) + self.graph.model.max_unit_w_p)
    interval_x = self.graph.math.calcUnitInterval(self.graph.model.scale_x)
    interval_x_point = self.graph.math.getXPointFromX(interval_x, self.min_x_point)
    min_x_i = (-w/2 + t_x) / interval_x_point
    max_x_i = (w/2 + t_x) / interval_x_point

    self.min_y_point = ((font_height / 2) + self.graph.model.max_unit_h_p)
    interval_y = self.graph.math.calcUnitInterval(self.graph.model.scale_y)
    interval_y_point = self.graph.math.getYPointFromY(interval_y, self.min_y_point)
    min_y_i = (-h/2 + t_y) / interval_y_point
    max_y_i = (h/2 + t_y) / interval_y_point

    # Plot the x units and grid if allowed
    if min_x_i == 0.0: min_x_i = 1e-100
    i_x = (abs(min_x_i) / min_x_i) * math.floor(abs(min_x_i))
    while i_x <= max_x_i:
      unit = interval_x * i_x
      x = interval_x_point * i_x
      y = -font_height - w_p - 1
      m = 1
      p = 0

      if self.graph.gui.show_units.get():
        if not unit == 0:
          d_y = ((h/2) - (w_p * 2))
          n_t_y = t_y
          if d_y - abs(t_y) < 0.0:
            if t_y >= 0.0:
              n_t_y = d_y
            else:
              n_t_y = -d_y
              m = 0
              p = w_p * 2

          # Negative x-axis units
          self.displayUnit(-unit, (-x + t_x, m * y + n_t_y + p), unitFont, "center",\
                           unit_width, superscript_width, point_width, times_width)
          self.graph.math.plotNegXAxisUnitLine(x, w_p, t_x, n_t_y)
          # Positive x-axis units
          self.displayUnit(unit, (x + t_x, m * y + n_t_y + p), unitFont, "center",\
                           unit_width, superscript_width, point_width, times_width)
          self.graph.math.plotPosXAxisUnitLine(x, w_p, t_x, n_t_y)

      if self.graph.gui.show_grid.get():
          # y (negative vertical grid lines)
          if not unit == 0:
            self.graph.math.plotNegVGridLine(h, x, t_x)
          # y (positive vertical grid lines)
          if unit == 0 and min_x_i <= 0 and 0 <= max_x_i:
            if self.graph.gui.show_grid.get() and self.graph.gui.show_axes.get():
              self.graph.math.plotPosVGridLine(h, x, t_x)
          else: self.graph.math.plotPosVGridLine(h, x, t_x)

      i_x = i_x + 1

    # Plot the y units and grid if allowed
    if min_y_i == 0.0: min_y_i = 1e-100
    i_y = (abs(min_y_i) / min_y_i) * math.floor(abs(min_y_i))
    while i_y <= max_y_i:
      unit = interval_y * i_y
      x = -w_p - 1
      y = interval_y_point * i_y
      m = 1
      p = 0
      _align = "right"

      if self.graph.gui.show_units.get():
        if not unit == 0:
          d_x = (w/2) - (w_p * 2)
          n_t_x = t_x
          if d_x - abs(t_x) < 0.0:
            if t_x >= 0.0:
              n_t_x = d_x
            else:
              n_t_x = -d_x
              m = 0
              p = w_p * 2
              _align = "left"

          # Positive y-axis units
          self.displayUnit(unit, (m * x + n_t_x + p, y - (font_height / 2) + t_y), unitFont,\
                           _align, unit_width, superscript_width, point_width, times_width)
          self.graph.math.plotPosYAxisUnitLine(y, w_p, n_t_x, t_y)
          # Negative y-axis units
          self.displayUnit(-unit, (m * x + n_t_x + p, -y - (font_height / 2) + t_y), unitFont,\
                           _align, unit_width, superscript_width, point_width, times_width)
          self.graph.math.plotNegYAxisUnitLine(y, w_p, n_t_x, t_y)

      if self.graph.gui.show_grid.get():
        # x (positive horizontal grid lines)
        if unit == 0 and min_y_i <= 0 and 0 <= max_y_i:
          if self.graph.gui.show_grid.get() and self.graph.gui.show_axes.get():
            self.graph.math.plotPosHGridLine(w, y, t_y)
        else: self.graph.math.plotPosHGridLine(w, y, t_y)
        # x (negative horizontal grid lines)
        if not unit == 0:
          self.graph.math.plotNegHGridLine(w, y, t_y)

      i_y = i_y + 1

  def display(self):
    if not self.graph.model.busy:
      self.graph.model.busy = True
      self.graph.writer.clear()
      n = 3

      for i in range(n):
        str_ = f"Press spacebar to see current screen size or Esc to quit {n - i}"
        self.graph.writer.ht()
        w,h = self.graph.getWindowSize()
        self.graph.writer.penup()
        self.graph.writer.goto(0, (h//2) - 50)
        self.graph.writer.write(str_, align="center", font=("Courier", 10, "bold"))
        self.graph.screen.update()
        time.sleep(1)
        self.graph.writer.clear()
      self.graph.model.busy = False

  def see_screen_size(self):
    if not self.graph.model.busy:
      self.graph.model.busy = True
      self.removeArtifacts()
      n = 3

      for i in range(n):
        w,h = self.graph.getWindowSize()
        str_ = f"Current Window size: ({str(w)}, {str(h)}) {n - i}"
        self.graph.writer.ht()
        self.graph.writer.penup()
        self.graph.writer.goto(0, (h//2) - 50)
        self.graph.writer.write(str_, align="center", font=("Courier", 10, "bold"))
        self.graph.screen.update()
        time.sleep(1)
        self.graph.writer.clear()
      self.graph.model.busy = False

      self.display()
      self.graph.controller.updateController()

  def quit(self):
    if not self.graph.model.busy:
      quit_bool = messagebox.askyesno(title="Confirm exit", message="Do you really want to quit?")

      if quit_bool:
        self.graph.model.busy = True
        self.removeArtifacts()

        _, h = self.graph.getWindowSize()
        self.graph.writer.ht()
        self.graph.writer.penup()
        self.graph.writer.goto(0, (-h//2) + 50)
        str_ = f"Quitting..."
        font_ = font.Font(family="Courier", size=10, weight="bold", slant="italic")
        self.graph.writer.write(str_, align="center", font=font_)
        self.graph.screen.update()
        time.sleep(1)
        self.graph.writer.clear()

        self.graph.model.busy = False
        self.graph.tt.bye()



class GraphController():
  def __init__(self, graph: Graph):
    self.graph = graph
    self.press_time: str | None = None

    self.graph.screen.onkey(self.graph.view.see_screen_size, "space")
    self.graph.screen.onkey(self.graph.view.quit, "Escape")
    self.graph.screen.listen()
    self.graph.screen.onscreenclick(self.graph.view.addTurtleOnClick)
    self.graph.screen.cv.bind("<ButtonPress-1>", self.graph.math.execScreenDragStart)
    self.graph.screen.cv.bind("<ButtonRelease-1>", self.graph.math.execScreenDragEnd)
    self.graph.screen.cv.bind("<B1-Motion>", self.graph.math.execScreenDragMotion)
    self.graph.root.bind("<ButtonPress-1>", self.onButtonPress)
    self.graph.root.bind("<ButtonRelease-1>", self.onButtonRelease)

    self.graph.view.display()
    self.updateController()
    self.redraw_after_id = None
    self.graph.root.bind("<Configure>", lambda event: self.redraw(event))

  def redraw(self, _):
    # Cancel any pending delayed redraw calls
    if self.redraw_after_id is not None:
      self.graph.root.after_cancel(self.redraw_after_id)
    # Schedule new call
    self.redraw_after_id = self.graph.root.after(100, self.delayed_redraw)

  def delayed_redraw(self):
    self.updateController()

  def updateController(self):
    _, _ = self.graph.view.updateView()

  def onButtonPress(self, _):
    self.press_time = self.graph.root.after(1000, self.checkLongPress) # 1 second delay

  def onButtonRelease(self, _):
    # Cancel the long press check if the button is released before the time
    if self.press_time:
      self.graph.root.after_cancel(self.press_time)

  def checkLongPress(self):
    if self.graph.callback: self.graph.callback()


class GraphExecutableHandler():
  def __init__(self, graph: Graph):...



class GraphFunctions():
  def __init__(self, graph: Graph):...


class GraphPopup():
  """
  Creates a fully scrollable popup
  """

  def __init__(self, graph: Graph, title: str, content: Callable, id: int):
    self.graph = graph
    self.openPopup(title)
  
  def openPopup(self, title: str, id: int):
    # Popup
    self.popup = tk.Toplevel(self.graph.root)
    self.popup.title = title
    self.id = id
    self.popup.overrideredirect(True) # No window decorations (feels more like a popup)
    self.popup.rowconfigure(1, weight=1)
    self.popup.columnconfigure(0, weight=1)

    # Place it near the mouse
    self.mouse_xy = self.graph.root.winfo_pointerxy
    self.smartPositioning()

    # Top right close button
    top_frame = tk.Frame(self.popup)
    top_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    top_frame.columnconfigure(0, weight=1)
    tk.Button(top_frame, text="Close", command=self.popup.destroy)\
      .grid(row=0, column=1,sticky="e") # right-aligned


    # Popup canvas
    self.canvas = tk.Canvas(self.popup)
    self.canvas.grid(row=1, column=0, sticky="nsew")

    # Scroll bars (Initially hidden)
    self.v_scroll = ttk.Scrollbar(self.popup, orient="vertical", command=self.canvas.yview)
    self.h_scroll = ttk.Scrollbar(self.popup, orient="horizontal", command=self.canvas.xview)

    self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

    # Inner frame inside canvas
    self.scrollable_frame = tk.Frame(self.canvas)

    # Create a window inside the canvas for the frame
    self.window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

    # Track resizing
    self.scrollable_frame.bind("<Configure>", self.updateScrollbarsDebounced)
    self.canvas.bind("<Configure>", self.updateScrollbarsDebounced)

  def smartPositioning(self):
    self.popup.update_idletasks() # Make sure geometry info is correct
    mouse_x, mouse_y = self.mouse_xy
    _, _, screen_w, screen_h = get_usable_screen_size()
    w = self.popup.winfo_width()
    h = self.popup.winfo_height()
    x = min(mouse_x + 10, screen_w - w)
    y = min(mouse_y + 10, screen_h - h)
    self.popup.geometry(f"+{w}x{h}+{x}+{y}")
  
  def updateScrollbarsDebounced(self):
    if hasattr(self, "_scrollbar_after_id"):
      self.popup.after_cancel(self._scrollbar_after_id)
    self._scrollbar_after_id = self.popup.after(50, self.updateScrollbars)
  
  def updateScrollbars(self):
    # Recalculate scrollregion
    self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # Canvas size
    canvas_width = self.canvas.winfo_width()
    canvas_height = self.canvas.winfo_height()

    # Content size
    bbox = self.canvas.bbox("all")
    if bbox:
      content_width = bbox[2] - bbox[0]
      content_height = bbox[3] - bbox[1]
    else:
      content_width = content_height = 0
    
    # Show or hide vertical scrollbar
    if content_height > canvas_height:
      self.v_scroll.grid(row=0, column=1, sticky="ns")
    else: self.v_scroll.grid_remove()
    
    # Show or hide horizontal scrollbar
    if content_width > canvas_width:
      self.h_scroll.grid(row=1, column=0, sticky="ew")
    else:
      self.h_scroll.grid_remove()
    
    self.smartPositioning()



class GraphPopups():
  def __init__(self, graph: Graph):
    self.graph = graph
    self.popup_tree: dict[int, list[int]] = {} # {popup_id: [children_ids]}
    self.parent_map: dict[int, int| None] = {} # {child_id, parent_id}
    self.popups : list[GraphPopup] = []
    self.graph.root.bind_all("<Button-1>", self.handle_click_global, add="+")
    self.popup_id_counter = 0

  def openPopup(self, title: str, parent_popup_id: str | None, content: Callable):
    new_popup = GraphPopup(self.graph, title, content, self.popup_id_counter)
    self.popup_id_counter += 1
    self.register(new_popup, parent_popup_id)
    return new_popup

  def register(self, gpopup: GraphPopup, parent_id: str | None):
    self.popup_tree.setdefault(gpopup, [])
    if parent_id:
      self.popup_tree[parent_id].append(str(gpopup.id))
      self.parent_map[str(gpopup.id)] = parent_id
    
    # Destroy all children if popup is closed
    gpopup.popup.protocol("WM_DELETE_WINDOW", lambda: self.destroy_subtree(gpopup.id))
    if self.popup_tree == {}:
      self.popup_id_counter = 0
  
  def destroy_subtree(self, gpopup_id: int):
    destroyed_popup_ids: list[str] = []
    for child_id in self.popup_tree.get(gpopup_id):
      destroyed_popup_ids += self.destroy_subtree(child_id)
      
    try:
      gpopup = self.popups[gpopup_id]
      gpopup.popup.destroy()
      destroyed_popup_ids.append(gpopup_id)
      self.popups.remove(gpopup)
    except:
      pass
    
    self.popup_tree.pop(gpopup_id, None)
    self.parent_map.pop(gpopup_id, None)
    return list(set(destroyed_popup_ids))
    
    
  def get_popup_bounds(self, gpopup: GraphPopup):
    x1 = gpopup.popup.winfo_rootx()
    y1 = gpopup.popup.winfo_rooty()
    x2 = x1 + gpopup.popup.winfo_width()
    y2 = x2 + gpopup.popup.winfo_height()
    return x1, y1, x2, y2
  
  def handle_click_global(self, event):
    x, y = event.x_root, event.y_root

    clicked_popup = None
    for gpopup in self.popups:
      bx1, by1, bx2, by2 = self.get_popup_bounds(gpopup)
      if bx1 <= x <= bx2 and by1 <= y <= by2:
        clicked_popup = gpopup
        break
    
    if clicked_popup is None:
      # Clicked outside all popups, destroy entire tree
      self.closeAllPopups()
    else:
      # Clicked inside a popup, destroy its descendants only
      self.destroy_descendants(clicked_popup)
  
  def destroy_descendants(self, gpopup_id: int):
    destroyed_popup_ids: list[str] = []
    for child_id in self.popup_tree.get(gpopup_id, []):
      destroyed_popup_ids += self.destroy_subtree(child_id)
    
    return list(set(destroyed_popup_ids))
  
  def closeAllPopups(self):
    popup_ids: set[str] = {}
    for popup in self.popups:
      popup_ids.add(str(popup.id))
      
    for popup_id in popup_ids.copy():
      if popup_id in popup_ids:
        destroyed_popup_ids = self.destroy_subtree(popup_id)
        popup_ids.difference_update(destroyed_popup_ids)
    
    self.popup_id_counter = 0


class HelperFunction():...


def main():
  _ = Graph(tt)

  return "EVENTLOOP"


if __name__ == "__main__":
  msg = main()
  print(msg)
  tt.mainloop()