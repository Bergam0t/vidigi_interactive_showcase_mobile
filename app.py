import streamlit as st

st.set_page_config(layout="wide",
                   initial_sidebar_state="expanded",
                   page_title="Vidigi - Interactive Demo")

import pandas as pd

import plotly.express as px

from examples.ex_1_simplest_case.simulation_execution_functions import single_run, multiple_replications
from examples.ex_1_simplest_case.model_classes import Scenario, TreatmentCentreModelSimpleNurseStepOnly
from examples.distribution_classes import Normal

from vidigi.animation import animate_activity_log

import gc

st.title("Simple Interactive Treatment Step")

st.markdown(
    """
This interactive simulation shows the simplest use of the animated event log. The model simulates queueing for a nurse, being seen, and then exiting the system.

This simulation will run for 3 days, creating an animation frame every 5 minutes.

On changing the values of the sliders, you can click the button again to generate an updated animation.
    """
)

gc.collect()

col1, col2 = st.columns(2)

with col1:

    nurses = st.slider("👨‍⚕️👩‍⚕️ How Many Rooms/Nurses Are Available?", 1, 15, step=1, value=4)


    mean_arrivals_per_day = st.slider("🧍 How many patients should arrive per day on average?",
                                    10, 300,
                                    step=5, value=120)

    seed = st.slider("🎲 Set a random number for the computer to use",
                        1, 1000,
                        step=1, value=42)


    run_time_days = 3

    # run_time_days = st.slider("🗓️ How many days should we run the simulation for each time?",
    #                         1, 40,
    #                         step=1, value=10)

    n_reps = 1

with col2:

    consult_time = st.slider("⏱️ How long (in minutes) does a consultation take on average?",
                                5, 150, step=5, value=50)

    consult_time_sd = st.slider("🕔 🕣 How much (in minutes) does the time for a consultation usually vary by?",
                                5, 30, step=5, value=10)

    norm_dist = Normal(consult_time, consult_time_sd, random_seed=seed)
    norm_fig = px.histogram(norm_dist.sample(size=2500), height=150,
                            color_discrete_sequence=["#0c9e10"])

    norm_fig.update_layout(yaxis_title="", xaxis_title="Consultation Time<br>(Minutes)")

    norm_fig.update_xaxes(tick0=0, dtick=10, range=[0,
                                                    # max(norm_dist.sample(size=2500))
                                                    240
                                                    ])



    norm_fig.layout.update(showlegend=False,
                            margin=dict(l=0, r=0, t=0, b=0))

    st.markdown("#### Consultation Time Distribution")
    st.plotly_chart(norm_fig,
                    use_container_width=True,
                    config = {'displayModeBar': False})



# A user must press a streamlit button to run the model
button_run_pressed = st.button("Click here to run the simulation and generate the animation", type="primary")


if button_run_pressed:

    # add a spinner and then display success box
    with st.spinner('Simulating the treaatment centre...'):

        args = Scenario(manual_arrival_rate=60/(mean_arrivals_per_day/24),
                        n_cubicles_1=nurses,
                        random_number_set=seed,
                        trauma_treat_mean=consult_time,
                        trauma_treat_var=consult_time_sd)

        model = TreatmentCentreModelSimpleNurseStepOnly(args)

        # st.subheader("Single Run")

        # results_df = single_run(args)

        # st.dataframe(results_df)

        # st.subheader("Multiple Runs")

        df_results_summary, detailed_results = multiple_replications(
                        args,
                        n_reps=n_reps,
                        rc_period=run_time_days*24*60,
                        return_detailed_logs=True
                    )

        event_position_df = pd.DataFrame([
                    {'event': 'arrival', 'x':  50, 'y': 300, 'label': "Arrival" },

                    # Triage - minor and trauma
                    {'event': 'treatment_wait_begins', 'x':  205, 'y': 270, 'label': "Waiting for Treatment"  },
                    {'event': 'treatment_begins', 'x':  205, 'y': 170, 'resource':'n_cubicles_1', 'label': "Being Treated" },

                    {'event': 'exit', 'x':  270, 'y': 70, 'label': "Exit"}

                ])


        st.plotly_chart(
            animate_activity_log(
                event_log=detailed_results[detailed_results['rep']==1],
                event_position_df= event_position_df,
                limit_duration=run_time_days*24*60,
                scenario=args,
                debug_mode=True,
                every_x_time_units=5,
                include_play_button=True,
                icon_and_text_size=10,
                gap_between_entities=10,
                gap_between_rows=25,
                gap_between_resources=15,
                plotly_height=400,
                plotly_width=600,
                override_x_max=300,
                override_y_max=500,
                wrap_queues_at=15,
                step_snapshot_max=100,
                time_display_units="dhm",
                display_stage_labels=False,
                add_background_image="https://raw.githubusercontent.com/hsma-programme/Teaching_DES_Concepts_Streamlit/main/resources/Simplest%20Model%20Background%20Image%20-%20Horizontal%20Layout.drawio.png",
            ), use_container_width=False,
                config = {'displayModeBar': False}
        )

    st.caption(
        """
        Blue dots represent the nurses available in the system.

        Icons represent the individual entities moving through the system.

        Click the play button to set the animation running.

        Alternatively, click and drag the slider to jump to different points in the simulation.
        """
    )
