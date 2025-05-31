import gradio as gr
import pandas as pd
from datetime import datetime
import os

# Initialize storage for scores with proper column names
COLUMNS = ['timestamp', 'judge_name', 'team_name', 'go_live', 'usefulness', 'taste', 'problem_statement']

if not os.path.exists('scores.csv'):
    # Create empty DataFrame with proper columns
    df = pd.DataFrame(columns=COLUMNS)
    # Write to CSV with columns
    df.to_csv('scores.csv', index=False, mode='w')
elif os.path.getsize('scores.csv') == 0:
    # If file exists but is empty, write headers
    pd.DataFrame(columns=COLUMNS).to_csv('scores.csv', index=False, mode='w')

def calculate_final_score(go_live, usefulness, taste, problem_statement):
    # Calculate weighted score
    final_score = (
        (go_live * 0.30) + 
        (usefulness * 0.30) + 
        (taste * 0.20) + 
        (problem_statement * 0.20)
    ) * 20  # Convert to 100-point scale
    return round(final_score, 2)

def submit_score(judge_name, team_name, go_live, usefulness, taste, problem_statement):
    if not judge_name.strip():
        return "Please enter your name!", judge_name
    if not team_name:
        return "Please select a team!", judge_name
    
    try:
        # Read existing scores, if file is empty, create new DataFrame
        try:
            scores_df = pd.read_csv('scores.csv')
        except pd.errors.EmptyDataError:
            scores_df = pd.DataFrame(columns=COLUMNS)
        
        # Validate score ranges
        scores = [go_live, usefulness, taste, problem_statement]
        if any(score < 0 or score > 5 for score in scores):
            return "All scores must be between 0 and 5!", judge_name
        
        # Check for duplicate scoring
        if len(scores_df) > 0:
            duplicate = scores_df[
                (scores_df['judge_name'].str.lower() == judge_name.strip().lower()) & 
                (scores_df['team_name'] == team_name)
            ]
            if not duplicate.empty:
                # Remove previous score if exists
                scores_df = scores_df[
                    ~((scores_df['judge_name'].str.lower() == judge_name.strip().lower()) & 
                      (scores_df['team_name'] == team_name))
                ]
        
        # Add new score
        new_score = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'judge_name': judge_name.strip(),
            'team_name': team_name.strip(),
            'go_live': go_live,
            'usefulness': usefulness,
            'taste': taste,
            'problem_statement': problem_statement
        }
        
        scores_df = pd.concat([scores_df, pd.DataFrame([new_score])], ignore_index=True)
        scores_df.to_csv('scores.csv', index=False)
        
        return f"✅ Score submitted successfully for team {team_name}!", judge_name
    
    except Exception as e:
        return f"Error submitting score: {str(e)}", judge_name

def generate_report():
    try:
        scores_df = pd.read_csv('scores.csv')
        if len(scores_df) == 0:
            return "No scores submitted yet!"
        
        # Calculate average scores and number of judges per team
        team_stats = scores_df.groupby('team_name').agg({
            'judge_name': 'count',  # Count number of judges
            'go_live': 'mean',
            'usefulness': 'mean',
            'taste': 'mean',
            'problem_statement': 'mean'
        }).round(2)
        
        team_stats.rename(columns={'judge_name': 'num_judges'}, inplace=True)
        
        # Calculate final weighted scores
        team_stats['final_score'] = team_stats.apply(
            lambda x: calculate_final_score(x['go_live'], x['usefulness'], x['taste'], x['problem_statement']),
            axis=1
        )
        
        # Sort by final score
        team_stats = team_stats.sort_values('final_score', ascending=False)
        
        # Format report with better visualization
        report = "🏆 HACKATHON FINAL RANKINGS 🏆\n"
        report += "=" * 40 + "\n\n"
        
        for idx, (team, stats) in enumerate(team_stats.iterrows(), 1):
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "  "
            
            report += f"{medal} Rank #{idx}: {team}\n"
            report += "─" * 40 + "\n"
            report += f"📊 FINAL SCORE: {stats['final_score']:.1f}/100"
            report += f" (Scored by {int(stats['num_judges'])} judge{'s' if stats['num_judges'] > 1 else ''})\n\n"
            
            # Detailed scores with visual bars
            report += "Detailed Scores:\n"
            
            # Go Live (30%)
            bar_length = int(stats['go_live'] * 4)
            report += f"Go Live       (30%): {stats['go_live']}/5 {'█' * bar_length}{'░' * (20-bar_length)}\n"
            
            # Usefulness (30%)
            bar_length = int(stats['usefulness'] * 4)
            report += f"Usefulness   (30%): {stats['usefulness']}/5 {'█' * bar_length}{'░' * (20-bar_length)}\n"
            
            # Taste (20%)
            bar_length = int(stats['taste'] * 4)
            report += f"Taste        (20%): {stats['taste']}/5 {'█' * bar_length}{'░' * (20-bar_length)}\n"
            
            # Problem Statement (20%)
            bar_length = int(stats['problem_statement'] * 4)
            report += f"Problem Stmt (20%): {stats['problem_statement']}/5 {'█' * bar_length}{'░' * (20-bar_length)}\n"
            
            report += "\n" + "=" * 40 + "\n\n"
        
        # Enhanced summary footer
        report += f"Total Teams Evaluated: {len(team_stats)}\n"
        report += f"Total Scores Submitted: {len(scores_df)}\n"
        report += f"Number of Judges: {scores_df['judge_name'].nunique()}\n"
        report += f"Average Score: {team_stats['final_score'].mean():.1f}/100\n"
        report += f"Highest Score: {team_stats['final_score'].max():.1f}/100\n"
        
        # Add teams not yet scored
        unscored_teams = set(TEAM_NAMES) - set(team_stats.index)
        if unscored_teams:
            report += "\nTeams Not Yet Scored:\n"
            for team in sorted(unscored_teams):
                report += f"• {team}\n"
        
        return report
    
    except Exception as e:
        return f"Error generating report: {str(e)}"

# Define team names list
TEAM_NAMES = [
    "tehlaninayan7",
    "kya@karu.mai",
    "Sugarplum",
    "Bob the Builders AI",
    "permissionless",
    "LLM Ninjas",
    "MailMatch",
    "Ironold",
    "ChaiBiscuit",
    "Dostwriter",
    "Neural Babel",
    "Fluid",
    "Team 1",
    "fiction AI",
    "SOLOYOLO"
]

# Create Gradio interface
with gr.Blocks(title="Hackathon Judge", theme=gr.themes.Soft()) as app:
    gr.Markdown(
        """
        # 🏆 Hackathon Judging System
        ### Welcome to the hackathon judging portal! 
        Please enter your details and scores below.
        """
    )
    
    with gr.Group(visible=True):
        with gr.Row():
            with gr.Column(scale=1):
                judge_name = gr.Textbox(
                    label="Judge Name",
                    placeholder="Enter your name",
                    elem_classes="input-field"
                )
            with gr.Column(scale=1):
                team_name = gr.Dropdown(
                    label="Team Name",
                    choices=TEAM_NAMES,
                    elem_classes="input-field"
                )
    
    gr.Markdown(
        """
        ### Scoring Criteria
        Please rate each criterion on a scale of 0-5
        """
    )
    
    with gr.Group(visible=True):
        with gr.Row():
            with gr.Column():
                go_live = gr.Slider(
                    minimum=0,
                    maximum=5,
                    step=1,
                    label="Go Live Score (30%)",
                    info="Rate the project's completion and deployment readiness",
                    value=0
                )
                usefulness = gr.Slider(
                    minimum=0,
                    maximum=5,
                    step=1,
                    label="Usefulness Score (30%)",
                    info="Rate how useful and practical the solution is",
                    value=0
                )
            with gr.Column():
                taste = gr.Slider(
                    minimum=0,
                    maximum=5,
                    step=1,
                    label="Taste Score (20%)",
                    info="Rate the vibe and overall presentation",
                    value=0
                )
                problem_statement = gr.Slider(
                    minimum=0,
                    maximum=5,
                    step=1,
                    label="Problem Statement Score (20%)",
                    info="Rate how well impactful the problem statement is",
                    value=0
                )
    
    with gr.Row():
        submit_btn = gr.Button("Submit Scores", variant="primary", scale=2)
        report_btn = gr.Button("Generate Report", variant="secondary", scale=1)
    
    submit_output = gr.Textbox(label="Submission Status", show_label=False)
    
    gr.Markdown("### 📊 Final Rankings")
    report_output = gr.Textbox(
        label="Final Report",
        show_label=False,
        lines=10,
        container=True
    )
    
    # Submit button click handler
    submit_btn.click(
        submit_score,
        inputs=[judge_name, team_name, go_live, usefulness, taste, problem_statement],
        outputs=[submit_output, judge_name]
    )
    
    report_btn.click(
        generate_report,
        inputs=[],
        outputs=report_output
    )
    
    # Add custom CSS
    gr.Markdown(
        """
        <style>
        .gradio-container {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(to bottom right, #1a0000, #400000);
            color: #ffe2e2;
        }
        
        .input-field {
            border-radius: 8px;
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 0, 0, 0.1) !important;
            color: #fff !important;
        }
        
        .gr-group {
            border-radius: 16px;
            background-color: rgba(255, 0, 0, 0.05);
            border: 1px solid rgba(255, 0, 0, 0.1);
            padding: 24px;
            margin: 15px 0;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .gr-button {
            border-radius: 8px;
            margin: 10px 0;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .gr-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 0, 0, 0.2);
        }
        
        .gr-button.primary {
            background: linear-gradient(135deg, #ff0000, #cc0000);
            border: none;
        }
        
        .gr-button.secondary {
            background: rgba(255, 0, 0, 0.1);
            border: 1px solid rgba(255, 0, 0, 0.2);
        }
        
        .gr-form {
            gap: 20px;
        }
        
        /* Slider styling */
        .gr-slider {
            background-color: rgba(255, 0, 0, 0.1);
        }
        
        .gr-slider .handle {
            background: #ff0000;
            box-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
        }
        
        .gr-slider .track {
            background: linear-gradient(90deg, #ff0000, #cc0000);
        }
        
        /* Text elements */
        h1, h2, h3 {
            color: #fff !important;
            text-shadow: 0 2px 4px rgba(255, 0, 0, 0.2);
        }
        
        .gr-markdown {
            color: #ffe2e2 !important;
        }
        
        /* Report output styling */
        .gr-textbox {
            background-color: rgba(255, 0, 0, 0.05) !important;
            border: 1px solid rgba(255, 0, 0, 0.1) !important;
            color: #fff !important;
            font-family: 'Courier New', monospace;
        }
        
        /* Labels */
        label {
            color: #ffe2e2 !important;
        }
        
        /* Info text */
        .info {
            color: #ffb3b3 !important;
        }
        
        /* Dropdown styling */
        .gr-dropdown {
            background-color: rgba(255, 0, 0, 0.05) !important;
            border: 1px solid rgba(255, 0, 0, 0.1) !important;
            color: #fff !important;
            border-radius: 8px;
        }
        
        .gr-dropdown:focus {
            border-color: rgba(255, 0, 0, 0.3) !important;
        }
        
        .gr-dropdown option {
            background-color: #1a0000;
            color: #fff;
        }
        </style>
        """
    )

if __name__ == "__main__":
    app.launch(share=True) 