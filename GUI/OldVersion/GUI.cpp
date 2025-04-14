#include <ncurses.h>
#include <string>
#include <vector>
#include <cstdint>
#include <iomanip>
#include <sstream>

struct Parameter{
    std::string name;
    double value;
    uint8_t type;
};

struct Plugins{
    std::string name;
    std::vector<Parameter> parameters;
};

/*list of plugins and parameters
*When adding new plugins name the vector the plugin name in the .json file
*ex. std::vector<Parameter> "pluginname"  = {
*       param1,
*       param2,
*       param3
*}
* Types:
* 0 button:
* 1 fader:
* 2 bypass:
*/

std::vector<Parameter> reverb = {
    {"bypass", 1, 2},
    {"freeze", 0, 0},
    {"dry", 0.5, 1},
    {"wet", 0.5, 1},
    {"room_size", 0.5, 1},
    {"width", 0.5, 1},
    {"damp", 1, 1}
};

std::vector<Plugins> plugins = {
    {"reverb", reverb}
};

void initscreen(){
    initscr();              // Initialize ncurses screen
    cbreak();               // Disable line buffering
    noecho();               // Disable echoing of characters
    keypad(stdscr, TRUE);   // Enable keypad for arrow keys
    curs_set(FALSE);        // Dont show cursor

    // Check if the terminal supports color
    if (!(has_colors())) {
        endwin();
        printf("Your terminal does not support color\n");
    }
    // Initialize color pairs
    start_color();
    init_pair(1, COLOR_GREEN, COLOR_BLACK); // Color for filled levels
    init_pair(2, COLOR_WHITE, COLOR_BLACK); // Color for empty levels
    init_pair(3, COLOR_BLACK, COLOR_WHITE); // Inverted for selection

}

uint8_t draw_letter(int16_t y, int16_t x, char letter){
    switch (letter)
    {
    case 'a':
    case 'A':
        mvprintw(y, x, "    _    ");
        mvprintw(y+1, x, "   / \\   ");
        mvprintw(y+2, x, "  / _ \\  ");
        mvprintw(y+3, x, " / ___ \\ ");
        mvprintw(y+4, x, "/_/   \\_\\");
        return 9;
    case 'b':
    case 'B':
        mvprintw(y, x, " ____  ");
        mvprintw(y+1, x, "| __ ) ");
        mvprintw(y+2, x, "|  _ \\ ");
        mvprintw(y+3, x, "| |_) |");
        mvprintw(y+4, x, "|____/ ");
        return 7;
    case 'c':
    case 'C':
        mvprintw(y, x, "  ____ ");
        mvprintw(y+1, x, " / ___|");
        mvprintw(y+2, x, "| |    ");
        mvprintw(y+3, x, "| |___ ");
        mvprintw(y+4, x, " \\____|");
        return 7;
    case 'd':
    case 'D':
        mvprintw(y, x, " ____  ");
        mvprintw(y+1, x, "|  _ \\ ");
        mvprintw(y+2, x, "| | | |");
        mvprintw(y+3, x, "| |_| |");
        mvprintw(y+4, x, "|____/ ");
        return 7;
    case 'e':
    case 'E':
        mvprintw(y, x, " _____ ");
        mvprintw(y+1, x, "| ____|");
        mvprintw(y+2, x, "|  _|  ");
        mvprintw(y+3, x, "| |___ ");
        mvprintw(y+4, x, "|_____|");
        return 7;
    case 'f':
    case 'F':
        mvprintw(y, x, " _____ ");
        mvprintw(y+1, x, "|  ___|");
        mvprintw(y+2, x, "| |_   ");
        mvprintw(y+3, x, "|  _|  ");
        mvprintw(y+4, x, "|_|    ");
        return 7;
    case 'g':
    case 'G':
        mvprintw(y, x, "  ____ ");
        mvprintw(y+1, x, " / ___|");
        mvprintw(y+2, x, "| |  _ ");
        mvprintw(y+3, x, "| |_| |");
        mvprintw(y+4, x, " \\____|");
        return 7;
    case 'h':
    case 'H':
        mvprintw(y, x, " _   _ ");
        mvprintw(y+1, x, "| | | |");
        mvprintw(y+2, x, "| |_| |");
        mvprintw(y+3, x, "|  _  |");
        mvprintw(y+4, x, "|_| |_|");
        return 7;
    case 'i':
    case 'I':
        mvprintw(y, x, " ___ ");
        mvprintw(y+1, x, "|_ _|");
        mvprintw(y+2, x, " | | ");
        mvprintw(y+3, x, " | | ");
        mvprintw(y+4, x, "|___|");
        return 5;
    case 'j':
    case 'J':
        mvprintw(y, x, "     _ ");
        mvprintw(y+1, x, "    | |");
        mvprintw(y+2, x, " _  | |");
        mvprintw(y+3, x, "| |_| |");
        mvprintw(y+4, x, " \\___/ ");
        return 7;
    case 'k':
    case 'K':
        mvprintw(y, x, " _  __");
        mvprintw(y+1, x, "| |/ /");
        mvprintw(y+2, x, "| ' / ");
        mvprintw(y+3, x, "| . \\ ");
        mvprintw(y+4, x, "|_|\\_\\");
        return 7;
    case 'l':
    case 'L':
        mvprintw(y, x, " _     ");
        mvprintw(y+1, x, "| |    ");
        mvprintw(y+2, x, "| |    ");
        mvprintw(y+3, x, "| |___ ");
        mvprintw(y+4, x, "|_____|");
        return 7;
    case 'm':
    case 'M':
        mvprintw(y, x, " __  __ ");
        mvprintw(y+1, x, "|  \\/  |");
        mvprintw(y+2, x, "| |\\/| |");
        mvprintw(y+3, x, "| |  | |");
        mvprintw(y+4, x, "|_|  |_|");
        return 8;
    case 'n':
    case 'N':
        mvprintw(y, x, " _   _ ");
        mvprintw(y+1, x, "| \\ | |");
        mvprintw(y+2, x, "|  \\| |");
        mvprintw(y+3, x, "| |\\  |");
        mvprintw(y+4, x, "|_| \\_|");
        return 7;
    case 'o':
    case 'O':
        mvprintw(y, x, "  ___  ");
        mvprintw(y+1, x, " / _ \\ ");
        mvprintw(y+2, x, "| | | |");
        mvprintw(y+3, x, "| |_| |");
        mvprintw(y+4, x, " \\___/ ");
        return 7;
    case 'p':
    case 'P':
        mvprintw(y, x, " ____  ");
        mvprintw(y+1, x, "|  _ \\ ");
        mvprintw(y+2, x, "| |_) |");
        mvprintw(y+3, x, "|  __/ ");
        mvprintw(y+4, x, "|_|    ");
        return 7;
    case 'q':
    case 'Q':
        mvprintw(y, x, "  ___  ");
        mvprintw(y+1, x, " / _ \\ ");
        mvprintw(y+2, x, "| | | |");
        mvprintw(y+3, x, "| |_| |");
        mvprintw(y+4, x, " \\__\\_\\");
        return 7;
    case 'r':
    case 'R':
        mvprintw(y, x, " ____  ");
        mvprintw(y+1, x, "|  _  \\");
        mvprintw(y+2, x, "| |_) |");
        mvprintw(y+3, x, "|  _ < ");
        mvprintw(y+4, x, "|_| \\_\\");
        return 7;
    case 's':
    case 'S':
        mvprintw(y, x, " ____  ");
        mvprintw(y+1, x, "/ ___| ");
        mvprintw(y+2, x, "\\___ \\ ");
        mvprintw(y+3, x, " ___) |");
        mvprintw(y+4, x, "|____/ ");
        return 7;
    case 't':
    case 'T':
        mvprintw(y, x, " _____ ");
        mvprintw(y+1, x, "|_   _|");
        mvprintw(y+2, x, "  | |  ");
        mvprintw(y+3, x, "  | |  ");
        mvprintw(y+4, x, "  |_|  ");
        return 7;
    case 'u':
    case 'U':
        mvprintw(y, x, " _   _ ");
        mvprintw(y+1, x, "| | | |");
        mvprintw(y+2, x, "| | | |");
        mvprintw(y+3, x, "| |_| |");
        mvprintw(y+4, x, " \\___/ ");
        return 7;
    case 'v':
    case 'V':
        mvprintw(y, x, "__     __");
        mvprintw(y+1, x, "\\ \\   / /");
        mvprintw(y+2, x, " \\ \\ / / ");
        mvprintw(y+3, x, "  \\ V /  ");
        mvprintw(y+4, x, "   \\_/   ");
        return 9;
    case 'w':
    case 'W':
        mvprintw(y, x, "__        __");
        mvprintw(y+1, x, "\\ \\      / /");
        mvprintw(y+2, x, " \\ \\ /\\ / / ");
        mvprintw(y+3, x, "  \\ V  V /  ");
        mvprintw(y+4, x, "   \\_/\\_/   ");
        return 12;
    case 'x':
    case 'X':
        mvprintw(y, x, "__  __");
        mvprintw(y+1, x, "\\ \\/ /");
        mvprintw(y+2, x, " \\  / ");
        mvprintw(y+3, x, " /  \\ ");
        mvprintw(y+4, x, "/_/\\_\\");
        return 6;
    case 'y':
    case 'Y':
        mvprintw(y, x, "__   __");
        mvprintw(y+1, x, "\\ \\ / /");
        mvprintw(y+2, x, " \\ V / ");
        mvprintw(y+3, x, "  | |  ");
        mvprintw(y+4, x, "  |_|  ");
        return 7;
    case 'z':
    case 'Z':
        mvprintw(y, x, " _____");
        mvprintw(y+1, x, "|__  /");
        mvprintw(y+2, x, "  / / ");
        mvprintw(y+3, x, " / /_ ");
        mvprintw(y+4, x, "/____|");
        return 6;
    case '1':
        mvprintw(y, x, " _ ");
        mvprintw(y+1, x, "/ |");
        mvprintw(y+2, x, "| |");
        mvprintw(y+3, x, "| |");
        mvprintw(y+4, x, "|_|");
        return 3;
    case '2':
        mvprintw(y, x, " ____  ");
        mvprintw(y+1, x, "|___ \\ ");
        mvprintw(y+2, x, "  __) |");
        mvprintw(y+3, x, " / __/ ");
        mvprintw(y+4, x, "|_____|");
        return 7;
    case '3':
        mvprintw(y, x, " _____ ");
        mvprintw(y+1, x, "|___ / ");
        mvprintw(y+2, x, "  |_ \\ ");
        mvprintw(y+3, x, " ___) |");
        mvprintw(y+4, x, "|____/ ");
        return 7;
    case '4':
        mvprintw(y, x, " _  _   ");
        mvprintw(y+1, x, "| || |  ");
        mvprintw(y+2, x, "| || |_ ");
        mvprintw(y+3, x, "|__   _|");
        mvprintw(y+4, x, "   |_|  ");
        return 8;
    case '5':
        mvprintw(y, x, " ____  ");
        mvprintw(y+1, x, "| ___| ");
        mvprintw(y+2, x, "|___ \\ ");
        mvprintw(y+3, x, " ___) |");
        mvprintw(y+4, x, "|____/ ");
        return 7;
    case '6':
        mvprintw(y, x, "  __   ");
        mvprintw(y+1, x, " / /_  ");
        mvprintw(y+2, x, "| '_ \\ ");
        mvprintw(y+3, x, "| (_) |");
        mvprintw(y+4, x, " \\___/ ");
        return 7;
    case '7':
        mvprintw(y, x, " _____ ");
        mvprintw(y+1, x, "|___  |");
        mvprintw(y+2, x, "   / / ");
        mvprintw(y+3, x, "  / /  ");
        mvprintw(y+4, x, " /_/   ");
        return 7;
    case '8':
        mvprintw(y, x, "  ___  ");
        mvprintw(y+1, x, " ( _ ) ");
        mvprintw(y+2, x, " / _ \\ ");
        mvprintw(y+3, x, "| (_) |");
        mvprintw(y+4, x, " \\___/ ");
        return 7;
    case '9':
        mvprintw(y, x, "  ___  ");
        mvprintw(y+1, x, " / _ \\ ");
        mvprintw(y+2, x, "| (_) |");
        mvprintw(y+3, x, " \\__, |");
        mvprintw(y+4, x, "   /_/ ");
        return 7;

    case '0':
        mvprintw(y, x, "  ___  ");
        mvprintw(y+1, x, " / _ \\ ");
        mvprintw(y+2, x, "| |/| |");
        mvprintw(y+3, x, "| |/| |");
        mvprintw(y+4, x, " \\___/ ");
        return 7;

    case '.':
        mvprintw(y, x, "   ");
        mvprintw(y+1, x, "   ");
        mvprintw(y+2, x, "   ");
        mvprintw(y+3, x, " _ ");
        mvprintw(y+4, x, "(_)");
        return 3;
    
    case '^':
        mvprintw(y, x, "    __    ");
        mvprintw(y+1, x, "   /  \\   ");
        mvprintw(y+2, x, "  / /\\ \\  ");
        mvprintw(y+3, x, " / /  \\ \\ ");
        mvprintw(y+4, x, "/_/    \\ \\");
        return 10;
        

    default:
        mvprintw(y, x, " ");
        mvprintw(y+1, x, " ");
        mvprintw(y+2, x, " ");
        mvprintw(y+3, x, " ");
        mvprintw(y+4, x, " ");
        return 1;
    }
    return -1;
}

std::string formatFloatToDecimals(double value) {
    std::ostringstream stream;
    stream << std::fixed << std::setprecision(2) << value;
    std::string result = stream.str();

    if (result[0] == '0' && result[1] == '.') {
        result.erase(0, 1);  // Remove the first character '0'
    }
    if(result[0] == '1'){
        result = "        1";
    }

    return result;
}


void draw_vertical_fader(int16_t y, int16_t x, Parameter parameter) {
    // Draw each level of the fader with appropriate color
    int i;
    for(i = 0; i < 20-(parameter.value * 100)/5; i++){
        mvprintw(y + i, x, "|       |");
    }
    for(; i < 20; i++){
        mvprintw(y + i, x, "|       |");
        attron(COLOR_PAIR(1));  // Filled level color
        mvprintw(y + i, x+1, "#######");
        attroff(COLOR_PAIR(1));
    }
    attroff(COLOR_PAIR(3));
}

void draw_button(int16_t y, int16_t x, double parameter, bool selected){
    if(selected){
        attron(COLOR_PAIR(3));
    }
    else{
        attron(COLOR_PAIR(2));
    }
    mvprintw(y , x, " ________ ");
    mvprintw(y+1 , x, "|        |");
    mvprintw(y+2 , x, "|        |");
    mvprintw(y+3 , x, "|        |");
    mvprintw(y+4 , x, "|________|");
    if(parameter  > 0){
        mvprintw(y+1 , x+1, "########");
        mvprintw(y+2 , x+1, "########");
        mvprintw(y+3 , x+1, "########");
        mvprintw(y+4 , x+1, "########");
    }
    attroff(COLOR_PAIR(3));
}

uint8_t draw_text(int16_t y, int16_t x, std::string text, bool selected){
    uint8_t color;
    uint16_t oldx = x;
    if(selected){
        color = 3;
    }
    else{
        color = 2;
    }
    attron(COLOR_PAIR(color));
    for(int i = 0; i < text.length(); i++){
        x = x + draw_letter(y, x, text[i]);
    }
    attroff(COLOR_PAIR(color));
    return x-oldx;
}

void send_osc_parameter(Plugins plugin, Parameter param){
    std::string command = "oscsend localhost 24024 /parameter/" + plugin.name + '/' + param.name + " f " + std::to_string(param.value);
    system(command.c_str());
}

void send_osc_bypass(Plugins plugin, Parameter param){
    std::string command = "oscsend localhost 24024 /bypass/" + plugin.name + " i " + std::to_string(param.value);
}

void draw_parameter_bypass(uint16_t y, uint16_t x, Parameter param, bool Selected){
    if(param.value == 0){
        draw_text(y,x,"on",Selected);
    }
    else{
        draw_text(y,x,"off",Selected);
    }
    draw_button(y,x+50, param.value, Selected);
}

void draw_line(uint16_t y, uint16_t x, uint16_t length){
    for(int i = 0; i < length; i++){
        mvprintw(y , x+i, "-");
    }
}

void draw_parameter_fader(uint16_t y, uint16_t x, Parameter param, bool Selected){
    draw_text(y, x, param.name.substr(0,4), Selected);
    draw_text(y,x+41, formatFloatToDecimals(param.value), Selected);
}

void draw_parameter_button(uint16_t y, uint16_t x, Parameter param, bool Selected){
    draw_text(y, x, param.name.substr(0,4), Selected);
    draw_button(y,x+50, param.value, Selected);
}

void draw_plugin(Plugins plugin, uint8_t cursor){
    draw_text(0,0,plugin.name, false);
    draw_line(5,0,60);
    for(int i = 0; i < plugin.parameters.size(); i++){
        if(reverb[i].type == 1){
            draw_parameter_fader(((6*i)+6), 0, plugin.parameters[i], cursor == i);
        }
        if(reverb[i].type == 0) {
            draw_parameter_button(((6*i)+6), 0, plugin.parameters[i], cursor == i);
        }
        if(reverb[i].type == 2){
            draw_parameter_bypass((6*i)+6, 0, plugin.parameters[i], cursor == i);
        }
        draw_line(((6*i) + 11),0,60);
    }
}

void draw_faderscreen(Parameter parameter){
    clear();
    uint16_t textsize = draw_text(0,1,parameter.name, false);
    draw_vertical_fader(6,(textsize/2)-4,parameter);
    draw_text(27, (textsize/2) - 9, formatFloatToDecimals(parameter.value), false);
}

void draw_screen_pluginmenu(Plugins plugin){
    
}
int main() {
    //Control variables
    uint8_t cursor = 0;
    uint8_t oldcursor;
    bool selected = false;
    
    initscreen();
    //Draw screen elements

    draw_plugin(plugins[0], cursor);
    
    while (true) {
        char  q = getch();
        switch (q)
        {
        case ',':
            if(selected){
                if(plugins[0].parameters[cursor].type == 1){
                    if(plugins[0].parameters[cursor].value > 0){
                        plugins[0].parameters[cursor].value = plugins[0].parameters[cursor].value - .01;
                        draw_faderscreen(plugins[0].parameters[cursor]);
                        send_osc_parameter(plugins[0], plugins[0].parameters[cursor]);
                    }
                }
                if(plugins[0].parameters[cursor].type == 0){
                    if(plugins[0].parameters[cursor].value == 1){
                        plugins[0].parameters[cursor].value = 0;
                        draw_plugin(plugins[0], cursor);
                        send_osc_parameter(plugins[0], plugins[0].parameters[cursor]);
                    }
                }
                if(plugins[0].parameters[cursor].type == 2){
                    if(plugins[0].parameters[cursor].value == 1){
                        plugins[0].parameters[cursor].value = 0;
                        clear();
                        draw_plugin(plugins[0], cursor);
                        send_osc_bypass(plugins[0], plugins[0].parameters[cursor]);
                    }
                }
            }
            else{
                oldcursor = cursor;
                if(cursor != 0){
                    cursor = cursor - 1;
                }
                if(oldcursor != cursor){
                    draw_plugin(plugins[0], cursor);
                }
            }
            break;

        case '.':
            if(selected == true){
                if(plugins[0].parameters[cursor].type == 1){
                    if(plugins[0].parameters[cursor].value < 1){
                        plugins[0].parameters[cursor].value = plugins[0].parameters[cursor].value + .01;
                        draw_faderscreen(plugins[0].parameters[cursor]);
                        send_osc_parameter(plugins[0], plugins[0].parameters[cursor]);
                    }
                    break;
                }
                if(plugins[0].parameters[cursor].type == 0){
                    if(plugins[0].parameters[cursor].value == 0){
                        plugins[0].parameters[cursor].value = 1;
                        draw_plugin(plugins[0], cursor);
                        send_osc_parameter(plugins[0], plugins[0].parameters[cursor]);
                    }
                    break;
                }
                if(plugins[0].parameters[cursor].type == 2){
                    if(plugins[0].parameters[cursor].value == 0){
                        plugins[0].parameters[cursor].value = 1;
                        clear();
                        draw_plugin(plugins[0], cursor);
                        send_osc_bypass(plugins[0], plugins[0].parameters[cursor]);
                    }
                }
            }
            else{
                oldcursor = cursor;
                if(cursor != 6){
                    cursor = cursor + 1;
                }
                if(oldcursor != cursor){
                    draw_plugin(plugins[0], cursor);
                }
            }
            break;

        case ' ':
            selected = !(selected);
            if(selected){
                if(plugins[0].parameters[cursor].type == 1){
                    draw_faderscreen(plugins[0].parameters[cursor]);
                }
            }
            if(selected == false && plugins[0].parameters[cursor].type == 1){
                clear();
                draw_plugin(plugins[0], cursor);
            }
            break;


        case 'q':
            endwin();  // End ncurses mode
            return 0;
        
        default:
            break;
        }
    }

    endwin();  // End ncurses mode
    return 0;
}
