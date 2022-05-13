def __append_project_sys_path():
    import os, sys
    from ..logger import get_logger
    module_file = "__init__.py"
    project_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    while os.path.exists(project_dir + os.sep + module_file):
        project_dir = os.path.dirname(project_dir)
    get_logger().info("[autosyspath] add a sys path: %s", project_dir)
    sys.path.append(project_dir)


__append_project_sys_path()
