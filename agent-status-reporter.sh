#!/bin/bash
# agent-status-reporter.sh - Generate automated status reports every 30 minutes

PROJECT_DIR="/Users/panglaohu/Downloads/DoubleBoatClawSystem"
cd "$PROJECT_DIR"

# Activate virtual environment
source venv/bin/activate

echo "📊 Setting up automated status reporting every 30 minutes..."
echo "📁 Project directory: $PROJECT_DIR"
echo "🕒 Report frequency: Every 30 minutes"
echo ""

# Create a function to generate the status report
generate_status_report() {
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    report_file="reports/agent_status_$(date +%Y%m%d_%H%M%S).txt"

    mkdir -p reports

    cat > "$report_file" << EOF
===============
🤖 AGENT TEAM STATUS REPORT
===============
Generated: $timestamp
Project: Deep Ocean Dual-Hull Vessel Intelligent Information System
Reporting Interval: 30 minutes

===============
📊 AGENT WORK PROGRESS
===============

EOF

    # Add progress summary
    if [ -f "progress_tracker.txt" ]; then
        echo "📋 Recent Progress Activity:" >> "$report_file"
        tail -20 progress_tracker.txt >> "$report_file"
        echo "" >> "$report_file"
    fi

    # Add file change statistics
    echo "📁 File Changes Summary:" >> "$report_file"
    echo "Python files: $(find src/ -name '*.py' | wc -l)" >> "$report_file"
    echo "Test files: $(find tests/ -name '*.py' | wc -l)" >> "$report_file"
    echo "Documentation files: $(find docs/ -name '*.md' | wc -l)" >> "$report_file"
    echo "" >> "$report_file"

    # Add TODO tracking
    echo "🔍 TODO Items Tracking:" >> "$report_file"
    todo_count=$(grep -r "TODO" src/ 2>/dev/null | wc -l)
    echo "Remaining TODOs in src/: $todo_count" >> "$report_file"

    if [ $todo_count -gt 0 ]; then
        grep -r "TODO" src/ 2>/dev/null | head -10 >> "$report_file"
        echo "" >> "$report_file"
    fi

    # Add print statement tracking
    echo "📝 Print Statements to Convert:" >> "$report_file"
    print_count=$(find src/ -name "*.py" -exec grep -l "print(" {} \; 2>/dev/null | wc -l)
    echo "Files with print() statements: $print_count" >> "$report_file"
    echo "" >> "$report_file"

    # Add exception tracking
    echo "⚠️  Exception Handling Status:" >> "$report_file"
    exception_count=$(find src/ -name "*.py" -exec grep -l "except Exception as e" {} \; 2>/dev/null | wc -l)
    echo "Files with basic exception handling: $exception_count" >> "$report_file"
    echo "" >> "$report_file"

    # Add sprint mode status
    echo "🏁 SPRINT MODE STATUS:" >> "$report_file"
    if [ -f "intensive_work.log" ]; then
        sprint_tasks=$(grep -c "SPRINT TASK COMPLETED" intensive_work.log)
        echo "Tasks completed in sprint: $sprint_tasks" >> "$report_file"

        current_intensity=$(tail -5 intensive_work.log | grep -c "HEAVY WORK\|MAXIMUM")
        echo "Current intensity level: HIGH ($current_intensity intense activities recorded recently)" >> "$report_file"
    else
        echo "Tasks completed in sprint: 0" >> "$report_file"
        echo "Current intensity level: MEDIUM" >> "$report_file"
    fi
    echo "" >> "$report_file"

    # Add completed tasks summary
    echo "✅ Recently Completed Tasks:" >> "$report_file"
    if [ -f "completed_tasks.txt" ]; then
        cat completed_tasks.txt >> "$report_file"
    else
        echo "No completed tasks recorded yet." >> "$report_file"
    fi

    echo "" >> "$report_file"
    echo "===============
📊 DETAILED METRICS
===============" >> "$report_file"

    # Add code written statistics
    echo "💻 CODE WRITTEN:" >> "$report_file"
    if [ -f "code_written_stats.log" ]; then
        code_files=$(tail -5 code_written_stats.log | wc -l)
        total_lines=$(awk '{sum += $8} END {print sum}' code_written_stats.log 2>/dev/null || echo 0)
        echo "  Files modified: $code_files" >> "$report_file"
        echo "  Lines of code added: $total_lines" >> "$report_file"
        echo "  Recent activity:" >> "$report_file"
        tail -3 code_written_stats.log >> "$report_file"
        echo "" >> "$report_file"
    fi

    # Add tests added statistics
    echo "🧪 TESTS ADDED:" >> "$report_file"
    if [ -f "tests_added_stats.log" ]; then
        test_files=$(awk '{sum += $7} END {print sum}' tests_added_stats.log 2>/dev/null || echo 0)
        test_functions=$(awk '{sum += $9} END {print sum}' tests_added_stats.log 2>/dev/null || echo 0)
        echo "  Test files added/modified: $test_files" >> "$report_file"
        echo "  Test functions added: $test_functions" >> "$report_file"
        echo "  Recent activity:" >> "$report_file"
        tail -3 tests_added_stats.log >> "$report_file"
        echo "" >> "$report_file"
    fi

    # Add design statistics
    echo "🛠️  DESIGN COMPLETED:" >> "$report_file"
    if [ -f "design_completed_stats.log" ]; then
        designs=$(awk '{sum += $7} END {print sum}' design_completed_stats.log 2>/dev/null || echo 0)
        echo "  Designs completed: $designs" >> "$report_file"
        echo "  Recent activity:" >> "$report_file"
        tail -3 design_completed_stats.log >> "$report_file"
        echo "" >> "$report_file"
    fi

    # Add research statistics
    echo "🔬 RESEARCH DONE:" >> "$report_file"
    if [ -f "research_done_stats.log" ]; then
        research_hours=$(awk '{sum += $7} END {print sum}' research_done_stats.log 2>/dev/null || echo 0)
        topics=$(awk '{sum += $9} END {print sum}' research_done_stats.log 2>/dev/null || echo 0)
        echo "  Research hours: $research_hours" >> "$report_file"
        echo "  Research topics: $topics" >> "$report_file"
        echo "  Recent activity:" >> "$report_file"
        tail -3 research_done_stats.log >> "$report_file"
        echo "" >> "$report_file"
    fi

    echo "" >> "$report_file"
    echo "=================" >> "$report_file"
    echo "END OF REPORT" >> "$report_file"
    echo "=================" >> "$report_file"

    # Log to console as well
    echo "✅ Status report generated: $report_file"
    echo "📈 Current progress tracked in progress_tracker.txt"

    # Append to a cumulative report
    echo "Report file: $report_file" >> agent_reports_log.txt
}

# Create the completed tasks file if it doesn't exist
touch completed_tasks.txt

# Create the reports log
touch agent_reports_log.txt

echo "🚀 Starting 30-minute status reporting cycle..."
echo "Reports will be saved to the 'reports/' directory."

# Main reporting loop
while true; do
    generate_status_report

    # Show current status
    echo ""
    echo "📊 Current status summary:"
    if [ -f "progress_tracker.txt" ]; then
        echo "Latest progress activity:"
        tail -5 progress_tracker.txt
    fi
    echo ""
    echo "Next report in 30 minutes..."
    echo "Press Ctrl+C to stop reporting"
    echo ""

    # Sleep for 30 minutes (1800 seconds)
    sleep 1800
done