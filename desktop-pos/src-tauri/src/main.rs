// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;

/// Tauri command: get app version
#[tauri::command]
fn get_app_version(app_handle: tauri::AppHandle) -> String {
    app_handle.package_info().version.to_string()
}

/// Tauri command: get app name
#[tauri::command]
fn get_app_name(app_handle: tauri::AppHandle) -> String {
    app_handle.package_info().name.clone()
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![get_app_version, get_app_name])
        .run(tauri::generate_context!())
        .expect("error while running Tauri application");
}
