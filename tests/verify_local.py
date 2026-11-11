"""Run repository checks without Studio, network access, saves or publication.

Pure/mocked suites and compilation cannot prove live microphones, Roblox physics,
UI layout, real persistence or multiplayer performance. See manual playtest list.
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true', help='Also build disposable review places and UI harnesses')
    args = parser.parse_args()
    env = os.environ.copy()
    env['PATH'] = env.get('PATH', '') + os.pathsep + '/opt/homebrew/bin'
    for tool in ('luau', 'luau-compile') + (('rojo',) if args.build else ()):
        if not shutil.which(tool, path=env['PATH']):
            raise SystemExit(f'Required local tool missing: {tool}')

    def run(command, quiet=False):
        subprocess.run(command, cwd=ROOT, env=env, check=True,
                       stdout=subprocess.DEVNULL if quiet else None)

    suites = sorted(path for path in (ROOT / 'tests').glob('*.luau')
                    if not path.name.startswith(('Studio', '.')))
    for path in suites:
        print(f'Checking {path.name}', flush=True)
        run(['luau', str(path)])
    mocked = ('profile_migration.py', 'profile_race.py', 'entitlements.py', 'destruction_service.py', 'microphone_lifecycle.py', 'animation_lifecycle.py', 'effect_cleanup.py', 'landmark_lifecycle.py', 'ambience_startup.py', 'performance_counts.py', 'hud_health.py', 'menu_cleanup.py', 'client_connections.py', 'resident_labels.py', 'interaction_recovery.py', 'city_map_marker.py', 'progress_label.py', 'settings_validation.py', 'knockout_recovery.py', 'combat_availability.py', 'respawn_state.py', 'target_readout.py', 'target_cover.py', 'sprint_state.py', 'dodge_cleanup.py', 'destruction_hint.py', 'npc_routes.py', 'sprint_input.py', 'movement_eligibility.py', 'npc_social.py', 'npc_audience.py', 'npc_greetings.py', 'npc_recovery.py', 'voice_toggle.py', 'npc_work.py', 'conversation_lifecycle.py', 'conversation_ownership.py', 'capture_blocking.py', 'player_departure.py', 'shutdown_saves.py', 'autosave_status.py', 'quest_prompt.py', 'quest_accept.py', 'quest_claim.py', 'pvp_rewards.py', 'ko_reward_cleanup.py')
    mocked += ('attack_audio.py', 'gameplay_audio.py', 'combat_healing.py', 'commerce.py', 'shop_rewards.py', 'practice_lane.py', 'shutdown_race.py', 'profile_recovery.py', 'recovery_notice.py', 'acquisition_lifetime.py', 'action_feedback.py')
    mocked += ('voice_notice_lifecycle.py',)
    mocked += ('save_notification_priority.py', 'third_person.py', 'beam_readout.py', 'boost_purchase_ui.py', 'developer_tools.py', 'developer_tools_ui.py', 'challenge_retirement.py', 'quest_catalog_ui.py', 'dodge_effect.py', 'style_controls.py', 'minimap.py', 'training_roam.py', 'beam_audio_levels.py', 'beam_audio_cadence.py', 'compact_city_draft.py', 'compact_city_map.py', 'compact_world.py', 'compact_integration.py', 'compact_review_fixture.py', 'compact_guidance.py', 'microphone_notice.py', 'voice_stop_rate_limit.py', 'combat_quests.py')
    for name in mocked:
        print(f'Checking {name} (mocked services)', flush=True)
        run([sys.executable, str(ROOT / 'tests' / name)])
    sources = sorted((ROOT / 'src').rglob('*.luau'))
    for path in sources:
        run(['luau-compile', str(path)], quiet=True)
    print(f'Compiled {len(sources)} production scripts; no Studio execution.', flush=True)
    if args.build:
        run([sys.executable, 'tests/build_candidate.py'])
        run([sys.executable, 'tests/build_sustained_review.py'])
        run([sys.executable, 'tests/build_studio_harness.py'])
        run([sys.executable, 'tests/build_shop_review.py'])
        run([sys.executable, 'tests/build_onboarding_review.py'])
        run([sys.executable, 'tests/build_notification_review.py'])
        run([sys.executable, 'tests/build_save_notice_review.py'])
        run([sys.executable, 'tests/build_quest_cards_review.py'])
        run([sys.executable, 'tests/build_style_review.py'])
        run([sys.executable, 'tests/build_minimap_review.py'])
        run([sys.executable, 'tests/build_compact_review.py'])
        run([sys.executable, 'tools/build_compact_city_draft.py'])
        for path in sorted((ROOT / 'build').glob('Studio*Harness.luau')) + [ROOT / 'build/StudioUIPreview.luau']:
            run(['luau-compile', str(path)], quiet=True)
        print('Built/compiled review fixtures; native runtime and UI appearance remain untested.', flush=True)
    print(f'PASS: {len(suites)} pure/synthetic suites, {len(mocked)} mocked-service suites, production compilation.')


if __name__ == '__main__':
    main()
