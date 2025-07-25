tell application "Finder"
    set currentDir to POSIX path of (container of ((container of (path to me))) as text)
end tell
tell application "Finder"
    make alias file to (POSIX file "/Applications") at (POSIX file "build/dmg_source_folder")
end tell