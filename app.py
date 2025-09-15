import os

from flask import Flask, request, render_template_string
from sympy import sympify
from math import inf

app = Flask(__name__)

def bisection(xl, xr, xm, fx):
    fxm = fx.subs("x", xm)
    fxr = fx.subs("x", xr)
    if fxm * fxr < 0:
        xl = xm
    else:
        xr = xm
    return xl, xr

# ------------------------------
# HTML template
# ------------------------------
HTML = """
<!DOCTYPE html>
<html>
  <head>
    <title>monmath | Bisection Calculator</title>
    <style>
      body { font-family: Arial; margin: 20px; }
      input { width: 150px; }
      h2 { color: darkblue; }
      pre { background-color: #f0f0f0; padding: 10px; }
    </style>
  </head>
  <body>
    <h2>Bisection Calculator</h2>
    <form method="post">
      Function f(x): <input type="text" name="fx" value="{{ fx }}" style="width:200px;"> = 0<br><br>
      Left (xl): <input type="text" name="xl" value="{{ xl }}"><br><br>
      Right (xr): <input type="text" name="xr" value="{{ xr }}"><br><br>
      Epsilon: <input type="text" name="epsilon" value="{{ epsilon }}"><br><br>
      <input type="submit" value="Compute">
    </form>
    <hr>
    {% if iterations %}
      <h3>Iterations:</h3>
      <pre>{{ iterations|join("\\n") }}</pre>
      <h3>Summary</h3>
      <p>Iteration number: {{ i }}</p>
      <p>x = {{ xm }}</p>
    {% endif %}
  </body>
</html>
"""

# ------------------------------
# Flask route
# ------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    iterations = []
    xm = None
    i = 0

    fx = xl = xr = epsilon = ""  # defaults for showing in form

    if request.method == "POST":
        try:
            # Step 0: เตรียมข้อมูล
            fx = sympify(request.form["fx"])
            xl = float(request.form["xl"])
            xr = float(request.form["xr"])
            epsilon = float(request.form["epsilon"])

            # Step 1: ทำทิ้ง 1 รอบ เพื่อเก็บค่า xₘ เก่า
            xm = (xl + xr) / 2
            xl, xr = bisection(xl, xr, xm, fx)

            # Step 2: Iterations
            criterion = inf
            while criterion > epsilon:
                xmnew = (xl + xr) / 2
                xl, xr = bisection(xl, xr, xmnew, fx)
                try:
                    criterion = abs((xmnew - xm) / xmnew)
                except ZeroDivisionError:
                    iterations.append(f"Stopped at Iteration {i}: Division by zero occurred.")
                    break
                iterations.append(f"Iteration {i}: xm = {xmnew}, criterion = {criterion}")
                xm = xmnew
                i += 1
        # กรณี User ทะลึ่งใส่ค่ามั่ว
        except Exception as e:
            iterations.append(f"Error: {e}")

    return render_template_string(
        HTML, iterations=iterations, i=i, xm=xm, fx=fx, xl=xl, xr=xr, epsilon=epsilon
    )

# ------------------------------
# Run app
# ------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # default 5000 for local
    app.run(host="0.0.0.0", port=port)