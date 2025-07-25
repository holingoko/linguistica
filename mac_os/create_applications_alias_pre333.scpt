tell application "Finder"
    set out_path to POSIX path of (container of ((container of (path to me))) as text) & "build/dmg_source_folder"
end tell