import os
from flask import Flask, request, render_template_string
from sympy import sympify
from math import inf

app = Flask(__name__)

def bisection_step(xl, xr, xm, fx):
    fxm = fx.subs("x", xm)
    fxr = fx.subs("x", xr)
    if fxm == 0:
        return xm, xm, True
    if fxm * fxr < 0:
        xl = xm
    else:
        xr = xm
    return xl, xr, False

HTML = """
<!DOCTYPE html>
<html>
  <head>
    <title>monmath | Bisection Calculator</title>
    <style>
      body { font-family: Arial; margin: 0; padding: 0; background-color: #f9f9f9; }
      input { width: 150px; }
      h2 { color: darkblue; margin-top: 0; }
      pre { background-color: #f0f0f0; padding: 10px; }
      
      /* Header bar */
      .header {
        background-color: darkblue;
        color: white;
        padding: 15px 20px;
        font-weight: bold;
        font-size: 24px;
      }

      .container {
        margin: 20px;
      }
    </style>
  </head>
  <body>
    <div class="header">monmath.com</div>
    <div class="container">
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
    </div>
  </body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    fx = xl = xr = epsilon = ""
    xm = None
    iterations = []
    i = 0

    if request.method == "POST":
        try:
            # Step 0: เตรียมข้อมูล
            fx = sympify(request.form["fx"])
            xl = float(request.form["xl"]); xl_input = xl
            xr = float(request.form["xr"]); xr_input = xr
            epsilon = float(request.form["epsilon"])

            # Step 1: ทำทิ้ง 1 รอบ เพื่อเก็บค่า xₘ
            xm = (xl + xr) / 2
            xl, xr, found_root = bisection_step(xl, xr, xm, fx)
            if found_root:
                iterations.append(f"Exact root found at Iteration {i}: x = {xm}")
            else:
                # Step 2: Iteration
                criterion = inf
                while criterion > epsilon:
                    i += 1
                    xmnew = (xl + xr) / 2
                    xl, xr, found_root = bisection_step(xl, xr, xmnew, fx)
                    if found_root:
                        iterations.append(f"Exact root found at Iteration {i}: x = {xmnew}")
                        xm = xmnew
                        break
                    try:
                        criterion = abs((xmnew - xm) / xmnew)
                    except ZeroDivisionError:
                        iterations.append(f"Stopped at Iteration {i}: Division by zero occurred.")
                        break
                    iterations.append(f"Iteration {i}: xm = {xmnew}, criterion = {criterion}")
                    xm = xmnew
            xl = xl_input
            xr = xr_input
        except Exception as e:
            iterations.append(f"Error: {e}")

    return render_template_string(
        HTML, iterations=iterations, i=i, xm=xm, fx=fx, xl=xl, xr=xr, epsilon=epsilon
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)