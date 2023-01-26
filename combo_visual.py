import numpy as np
from stl import mesh
import plotly.graph_objects as go
from temperatures import arr
import plotly.express as px
import wget


def stl2mesh3d(stl_mesh):
    """ Функция конвертации STL модели в Mesh3d """

    p, q, r = stl_mesh.vectors.shape
    vertices, ixr = np.unique(stl_mesh.vectors.reshape(p * q, r), return_inverse=True, axis=0)
    I = np.take(ixr, [3 * k for k in range(p)])
    J = np.take(ixr, [3 * k + 1 for k in range(p)])
    K = np.take(ixr, [3 * k + 2 for k in range(p)])
    return vertices, I, J, K


def visualization():
    """ Визуализация модели .STL """

    my_mesh = mesh.Mesh.from_file('model.stl')
    vertices, I, J, K = stl2mesh3d(my_mesh)
    x, y, z = vertices.T
    colorscale = [[0, '#555555'], [1, '#e5dee5']]

    fig.add_trace(go.Mesh3d(
        x=x + 2500,
        y=y + 250,
        z=z + 250,
        i=I,
        j=J,
        k=K,
        flatshading=True,
        colorscale=colorscale,
        intensity=z,
        name='LOTUS STHE',
        showscale=False,
    ))
    fig.update_layout(
        paper_bgcolor='rgb(1,1,1)',
        title_text="Mesh3d LOTUS STHE",
        title_x=0.5,
        font_color='white',
        width=1000,
        height=700,
        scene_camera=dict(eye=dict(x=1.25, y=-1.25, z=1)),
        scene_xaxis_visible=False,
        scene_yaxis_visible=False,
        scene_zaxis_visible=False,
    )


def interpolation(t1, x1, t2, x2, x):
    """ Функция интерполяции по 4 значениям """

    t = (x - x1) * (t2 - t1) / (x2 - x1) + t1
    return t


def define_shell_temperature_by_interpolation(x, y, z):
    """ Интерполяция по промежуточным значениям """

    coords = (x, y, z)

    pre_arr_by_x = []
    for i in arr:
        if (i[0][0] <= coords[0] < i[1][0]) or (i[1][0] <= coords[0] < i[0][0]):
            pre_arr_by_x.append(i)

    pre_arr_by_y = []
    for i in pre_arr_by_x:
        if i[0][1] <= coords[1] < i[1][1]:
            pre_arr_by_y.append(i)

    pre_arr_by_z = []
    for i in pre_arr_by_y:
        if i[0][2] <= coords[2] < i[1][2]:
            pre_arr_by_z.append(i)

    t1 = pre_arr_by_z[0][2]
    t2 = pre_arr_by_z[0][3]
    y1 = pre_arr_by_z[0][0][1]
    y2 = pre_arr_by_z[0][1][1]
    y = coords[1]
    t = interpolation(t1, y1, t2, y2, y)
    return t


if __name__ == "__main__":
    URL = "https://lotus1.org/content/blocks/files/sthe_stl_model_22606154.stl"
    response = wget.download(URL, "model.stl")

    x = 650
    y = 410
    z = 300
    print(define_shell_temperature_by_interpolation(x, y, z))

    fig = go.Figure()
    visualization()

    colorscale = 'YlOrRd_r'
    palette = px.colors.sequential.YlOrRd_r

    all_temp = set()
    for t in arr:
        all_temp.add(t[2])
        all_temp.add(t[3])

    min_temp = int(min(all_temp))
    max_temp = int(max(all_temp))
    temp_gap = max_temp - min_temp + 1

    min_poss_temp = int(min_temp - temp_gap)
    max_poss_temp = int(max_temp + temp_gap)

    for n in arr:
        color_index = int((int((n[2] + n[3]) / 2) - min_poss_temp) * len(palette) / (max_poss_temp - min_poss_temp + 1))

        fig.add_trace(go.Mesh3d(
            x=np.array([n[0][0], n[0][0], n[1][0], n[1][0], n[0][0], n[0][0], n[1][0], n[1][0]]),
            y=np.array([n[0][1], n[1][1], n[1][1], n[0][1], n[0][1], n[1][1], n[1][1], n[0][1]]),
            z=np.array([n[0][2], n[0][2], n[0][2], n[0][2], n[1][2], n[1][2], n[1][2], n[1][2]]),
            alphahull=0,
            opacity=0.7,
            color=palette[color_index],
            flatshading=True,
            showlegend=False
        ))

        fig.add_trace(
            go.Scatter3d(
                x=np.array([n[0][0], n[0][0], n[0][0], n[1][0], n[1][0], n[1][0], n[1][0], n[0][0], n[0][0],
                            n[0][0], n[0][0], n[0][0], n[1][0], n[1][0], n[1][0], n[1][0], n[0][0]]),
                y=np.array([n[0][1], n[1][1], n[1][1], n[1][1], n[1][1], n[0][1], n[0][1], n[0][1], n[0][1],
                            n[0][1], n[1][1], n[1][1], n[1][1], n[1][1], n[0][1], n[0][1], n[0][1]]),
                z=np.array([n[0][2], n[0][2], n[1][2], n[1][2], n[0][2], n[0][2], n[1][2], n[1][2], n[0][2],
                            n[1][2], n[1][2], n[0][2], n[0][2], n[1][2], n[1][2], n[0][2], n[0][2]]),
                mode="lines",
                line=dict(
                    color='#A9A9A9',
                    width=6,
                ),
                showlegend=False,
            ))

    fig.add_trace(go.Scatter3d(
        x=[None],
        y=[None],
        z=[None],
        mode='markers',
        marker=dict(
            colorscale=colorscale,
            showscale=True,
            cmin=min_poss_temp,
            cmax=max_poss_temp,
            colorbar=dict(
                title='Temperature',
                thickness=50,
                tickvals=[min_poss_temp, min_temp, max_temp, max_poss_temp],
                ticktext=[min_poss_temp, min_temp, max_temp, max_poss_temp])
        ),
        hoverinfo='none',
        showlegend=False,
    ))

    fig.show()
