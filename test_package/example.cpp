#include <sqlite3.h>

int main()
{
	sqlite3 *database;
	sqlite3_open(":memory:", &database);
	sqlite3_close(database);
	
	return 0;
}
